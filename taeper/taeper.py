from __future__ import print_function, division
import warnings
import numpy as np
import os
import sys
import argparse
import shutil
import time
from datetime import datetime
import pickle
from typing import Tuple, Generator, List

# suppress annoying warning coming from this libraries use of h5py
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from ont_fast5_api import fast5_file as fast5


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
    """Calculates the time when the read finished sequencing.

    :param filepath: full path to fast5 file

    :returns Seconds between experiment start and read finishing.
    """
    time_info = extract_time_fields(filepath)
    experiment_start = time_info['exp_start_time']

    # adjust for the sampling rate of the channel
    sample_length = time_info['start_time'] + time_info['duration']
    finish = sample_length / time_info['sampling_rate']

    return experiment_start + finish


def scantree(path: str) -> Generator:
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            for dir_entry in scantree(entry.path):
                yield dir_entry
        else:
            yield entry


def gather_files_and_times(reads_dir: str) -> List[Tuple[float, str]]:
    """Walks down the read directory and gathers the time information for each
    fast5 read.

    :param reads_dir: Path to directory holding fast5 reads.
    :return: A list of tuples where trhe first element is the timestamp and the
    second element is the file path for the read asscoiated with it.

    """
    staging_list = []

    for root, dirs, files in os.walk(reads_dir):
        for i, filename in enumerate(files):
            if filename.endswith(".fast5"):
                filepath = os.path.join(root, filename)
                try:
                    timestamp = calculate_timestamp(filepath)
                    staging_list.append((timestamp, filepath))
                except IOError as err:
                    # some fast5 files can be corrupted
                    sys.stderr.write("{} not processed. Error "
                                     "encountered: {}".format(filepath, err))
            perc = round(float(i) / len(files) * 100, 1)
            print(
                ">>> {0}% of the files processed in {1} directory...\t\t\t".format(
                    perc, root.split("/")[-1]), end='\r')
            sys.stdout.flush()
    print("\nAll files processed.")

    return staging_list


def generate_ordered_list(reads_dir: str) -> List[Tuple[float, str]]:
    """Returns a list that is sorted in ascending order by time.
    All timepoints are relative to the first entry which is time 0.

    :param reads_dir: Path to directory holding fast5 reads.

    :returns sorted_centred_staging_list: A list of tuples of time and path to
    file.

    """
    staging_list = gather_files_and_times(reads_dir)
    staging_list.sort()  # todo: benchmarking other sorting methods

    # make the first read "time 0" and all others relative to that
    start = staging_list[0][0]
    sorted_centred_staging_list = [(timestamp + (0 - start), filepath)
                                   for (timestamp, filepath) in staging_list]

    return sorted_centred_staging_list


def write_failed_files(files):
    """

    :param files:
    """
    with open('files_not_processed.txt', 'w') as fo:
        fo.write("filepath\terror_message\n")
        for entry in files:
            fo.write("{0}\t{1}\n".format(entry[0], entry[1]))


def write_pickle(xs):
    """Write a given list to file as a pickle."""
    pickle_path = "file_order.p"

    # write the ordered list to a pickled file incase order is required later
    with open(pickle_path, 'w') as fp:
        pickle.dump(xs, fp)


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


def open_pickle(file_):
    """Open a pickle file and load the list contained within."""
    with open(file_, 'rb') as fp:
        return pickle.load(fp)


def check_positive(val):
    val = float(val)
    if not val > 0:
        raise argparse.ArgumentTypeError("Scale must be a positive value, \
                greater than 0. Value given was {0}.".format(val))
    return val


def main(args):
    if args.input_dir:
        centred_list = generate_ordered_list(args.input_dir)
        np.save('file_order.npy', centred_list)
    else:
        centred_list = open_pickle(args.input_pickle)

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
