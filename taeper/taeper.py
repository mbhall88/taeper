from __future__ import print_function, division
import warnings
import numpy as np
import os
import sys
import argparse
import shutil
import time
import logging
from datetime import datetime
from typing import Generator, List, Tuple

# suppress annoying warning coming from this libraries use of h5py
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from ont_fast5_api import fast5_file as fast5


EXTENSION = '.fast5'


def _zulu_to_epoch_time(zulu_time: str) -> float:
    """Auxiliary function to parse Zulu time into epoch time"""
    epoch = datetime(1970, 1, 1)
    time_as_date = datetime.strptime(zulu_time, "%Y-%m-%dT%H:%M:%SZ")
    return (time_as_date - epoch).total_seconds()


def extract_time_fields(filepath: str) -> dict:
    """Extracts the time from a given fast5 file.

    :param filepath: full path to fast5 file.

    :returns fields: a dictionary containing the read start time,
    experiment start time, duration of read, and sampling rate of the
    channel.

    """
    fast5_info = fast5.Fast5Info(filepath)
    fast5_file = fast5.Fast5File(filepath)
    exp_start_time = fast5_file.get_tracking_id()['exp_start_time']
    sampling_rate = float(fast5_file.get_channel_info()['sampling_rate'])

    fields = {
        'exp_start_time': _zulu_to_epoch_time(exp_start_time),
        'sampling_rate': sampling_rate,
        'duration': float(fast5_info.read_info[0].duration),
        'start_time': float(fast5_info.read_info[0].start_time)
    }
    return fields


def calculate_timestamp(filepath: str) -> float:
    """Calculates the epoch time when the read finished sequencing.

    :param filepath: full path to fast5 file

    :returns Epoch time that the read finished sequencing
    """
    time_info = extract_time_fields(filepath)
    experiment_start = time_info['exp_start_time']

    # adjust for the sampling rate of the channel
    sample_length = time_info['start_time'] + time_info['duration']
    finish = sample_length / time_info['sampling_rate']

    return experiment_start + finish


def scantree(path: str, ext: str) -> Generator:
    """Recursively scans a directory and returns file paths ending in a given
    extension.

    :param path: Directory to scan.
    :param ext: Yield files with this extension.

    :returns Yields path to each file ending in extension.
    """
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            for nested_entry in scantree(entry.path, ext):
                yield nested_entry
        elif entry.is_file() and entry.name.endswith(ext):
            yield entry.path


def read_deposit(t, prev, file_, output_dir, scale):
    """Copies a file to a given directory with a delay.

    Args:
        t (float): Number of seconds to delay copy by.
        prev (float): Previous read's t variable. Subtract from current read
        to get pause time.
        file_ (str): Path to file to be copied.
        output_dir (str): Directory to copy file to.
        scale (float): Scale the delay time by a given amount.

    Returns:
        None: Copies the file but returns nothing.

    """
    # pause to simulate real time. scale pause accordingly
    time.sleep((t - prev) / scale)

    # copy file to designated folder
    if "/fail/" in file_.lower():
        fail_dir = os.path.join(output_dir, "fail/")
        if not os.path.exists(fail_dir):
            os.makedirs(fail_dir)
        shutil.copy2(file_, fail_dir)
    elif "/pass/" in file_.lower():
        pass_dir = os.path.join(output_dir, "pass/")
        if not os.path.exists(pass_dir):
            os.makedirs(pass_dir)
        shutil.copy2(file_, pass_dir)
    else:
        try:
            file_num = int(file_.split("/")[-2])
            dir_ = file_.split("/")[-2]
            this_dir = os.path.join(output_dir, dir_)
            if not os.path.exists(this_dir):
                os.makedirs(this_dir)
            shutil.copy2(file_, this_dir)
        except ValueError as e:
            shutil.copy2(file_, output_dir)


def check_positive(val):
    val = float(val)
    if not val > 0:
        raise argparse.ArgumentTypeError("Scale must be a positive value, \
                greater than 0. Value given was {0}.".format(val))
    return val


def generate_index(input_dir: str) -> List[Tuple[float, str]]:
    """Returns a list that is sorted in ascending order by time.
    All timepoints are relative to the first entry which is time 0.

    :param input_dir: Path to directory holding fast5 reads.

    :returns centred_list: A list of lists of time and path to file.

    """
    fast5_paths = scantree(input_dir, EXTENSION)
    paths_with_their_timestamps = []
    for f5_path in fast5_paths:
        try:
            timestamp = calculate_timestamp(f5_path)
            time_path_pair = [timestamp, f5_path]
            logging.debug(time_path_pair)
            paths_with_their_timestamps.append(time_path_pair)
        except OSError as err:
            logging.warning(" {} not processed. Error "
                            "encountered: {}\n".format(f5_path, err))

    # todo: benchmark other sorting algorithms
    paths_with_their_timestamps.sort()

    # unzip the list in order to use numpy ediff1d method
    timestamps, paths = zip(*paths_with_their_timestamps)
    # make the first read "time 0" and all others relative to that
    zero_centered_times = np.ediff1d(timestamps, to_begin=0)
    # zip times back with paths
    return list(zip(zero_centered_times.round(decimals=3), paths))
   


def main(args):
    if args.input_dir:
        centred_list = generate_index(args.input_dir)
        # np.save('file_order.npy', centred_list)
    else:
        # centred_list = open_pickle(args.input_pickle)
        pass
    # if no output directory was given, stop here.
    if not args.output_dir: return

    # start copying of files
    print("Starting transfer of files to {}".format(args.output_dir))

    # this will be subtracted from the time for each read
    prev_time = 0
    for i, (delay, filepath) in enumerate(centred_list):
        delay = float(delay)
        perc = round(float(i) / len(centred_list) * 100, 1)
        read_deposit(delay, prev_time, filepath, args.output_dir, args.scale)
        prev_time = delay
        print(">>> {}% of files transfered...".format(perc), end='\r')
        sys.stdout.flush()
    print("ALL READS DEPOSITED")
