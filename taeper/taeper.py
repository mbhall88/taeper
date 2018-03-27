# -*- coding: utf-8 -*-

"""Main module."""
from __future__ import print_function
from ont_fast5_api import fast5_file as Fast5
import numpy as np
import os
import sys
import argparse
import shutil
import time
from datetime import datetime, date
import pickle

try:
    from os import scandir
except ImportError:
    from scandir import scandir


def convert2epoch(t):
    """Auxiliary function to parse Zulu time into epoch time"""
    epoch = datetime(1970, 1, 1)
    return (datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ") - epoch).total_seconds()


# extract raw signal start time and duration, experiment start time, and
# sampling rate
def extract_time_fields(filepath):
    """Extracts the time from a given fast5 file.

    Args:
        filepath (str): full path to fast5 file.

    Returns:
        fields (dict): a dictionary containing the read start time,
        experiment start time, duration of read, and sampling rate of the
        channel.

    """
    fast5_info = Fast5.FastInfo(filepath)
    exp_start_time = fast5_info.get_tracking_id()['exp_start_time']
    sampling_rate = fast5_info.get_channel_info()['sampling_rate']

    fields = {
        'exp_start_time': exp_start_time,
        'sampling_rate': sampling_rate,
        'duration': fast5_info.read_info[0].duration,
        'start_time': fast5_info.read_info[0].start_time
    }

    return fields


# create field associated with each read that is seconds since first read
# scale this by scaling factor
def calculate_timestamp(info):
    """Calculates the time when the read finished sequencing.

    Args:
        info (dict): experiment start time, read start time, duration, and
        sampling rate.

    Returns:
        (float): seconds between experiment start and read finishing.
    """
    exp_start = info['exp_start_time']
    # adjust for the sampling rate of the channel
    finish = (info['start_time'] + info['duration']) / info['sampling_rate']
    return exp_start + finish


def associate_time(filepath):
    """Associates the seconds elapsed between the start of exp. and read
    finishing to the path for that read.

    Args:
        filepath (str): path to fast5 file.

    Returns:
        tuple(float, str): tuple representing the time in seconds and the path
        to the file.

    """
    t = calculate_timestamp(extract_time_fields(filepath))
    return (t, filepath)


def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            for entry in scantree(entry.path):
                yield entry
        else:
            yield entry


def generate_ordered_list(reads_dir, fail=True):
    """Returns a list that is sorted in ascending order by time.
    All timepoints are relative to the first entry which is time 0.

    Args:
        reads_dir (str): Path to directory holding fast5 reads.
        fail (bool): Whether to transfer files from the fail folder too.

    Returns:
        sorted_centred_staging_list (list[tuple(float, str)]): A list of
        tuples of time and path to file.

    """

    # function to make all times relative to first time which is 0.
    def _centre(xs):
        return map(lambda x: (float(x[0] + (0 - xs[0][0])), x[1]), xs)

    staging_list = []
    files_not_processed = []
    counter = 0

    for root, dirs, files in os.walk(reads_dir):
        if dirs and not fail:  # only pass folder
            dirs[:] = [d for d in dirs if d not in ["fail"]]
        for i, filename in enumerate(files):
            if filename.endswith(".fast5"):
                filepath = os.path.join(root, filename)
                try:
                    staging_list.append(associate_time(filepath))
                except IOError as e:
                    # some fast5 files can be corrupted
                    files_not_processed.append((filepath, e))
            perc = round(float(i) / len(files) * 100, 1)
            print(">>> {0}% of the files processed in {1} directory...\t\t\t" \
                  .format(perc, root.split("/")[-1]), end='\r')
            sys.stdout.flush()
    print("\nAll files processed.")

    # centre and sort the list so the first entry is time 0
    sorted_centred_staging_list = _centre(sorted(staging_list))

    if files_not_processed:
        write_failed_files(files_not_processed)

    return sorted_centred_staging_list


def write_failed_files(files):
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
    # example use of fast5 api
    # f5 = Fast5.Fast5File(fname)
    if args.input_dir:
        centred_list = generate_ordered_list(args.input_dir, args.fail)
        write_pickle(centred_list)
    else:
        centred_list = open_pickle(args.input_pickle)

    # if no output directory was given, stop here.
    if not args.output_dir: return

    # start copying of files
    print("Starting transfer of files to {}".format(args.output_dir))

    # this will be subtracted from the time for each read
    prev_time = 0
    for i, read in enumerate(centred_list):
        perc = round(float(i) / len(centred_list) * 100, 1)
        read_deposit(read[0], prev_time, read[1], args.output_dir, args.scale)
        prev_time = read[0]
        print(">>> {}% of files transfered...".format(perc), end='\r')
        sys.stdout.flush()
    print("ALL READS DEPOSITED")


