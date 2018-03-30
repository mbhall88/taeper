# -*- coding: utf-8 -*-

"""Console script for taeper."""
import sys
import argparse
import logging
from taeper import taeper


LOGGING_LEVELS = {
    0: "NOTSET",
    1: "CRITICAL",
    2: "ERROR",
    3: "WARNING",
    4: "INFO",
    5: "DEBUG"
}


def main():
    """Console script for taeper."""
    parser = argparse.ArgumentParser(
        description="Simulate the real-time depositing of Nanopore \
                        reads into a given folder, conserving the order they \
                        were processed during sequencing. If pass and fail \
                        folders do not exist in output_dir they will be created \
                        if detected in the file path for the fast5 file.")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-i", "--input_dir",
        help="Directory where files are located.",
        type=str)

    group.add_argument(
        "-p", "--input_pickle",
        help="Copy files based on a previously obtained pickle file. \
                        The pickle file should have been created by this program \
                        previously. Useful if program needs to be run muliple \
                        times for the same sample.",
        type=str)

    parser.add_argument(
        "-o", "--output_dir",
        help="Directory to copy the files to. If not specified, will \
                        generate the pickle file only. (Default = None)",
        type=str, default=None)

    parser.add_argument(
        "--scale",
        help="Amount to scale the timing by. i.e scale of 10 will \
                        deposit the reads 10x fatser than they were generated.\
                         (Default = 1.0)",
        type=float,
        default=1.0)

    parser.add_argument(
        "--log_level",
        help="Level of logging. 0 is none, 5 is for debugging. Default is 3 "
             "which will report warnings, errors, and critical information.",
        default=3,
        type=int,
        choices=range(6))

    args = parser.parse_args()

    # setup logging
    log_level = LOGGING_LEVELS.get(args.log_level)
    logging.basicConfig(level=log_level,
                        format='[%(asctime)s]:%(levelname)s:%(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    # it's business time
    taeper.main(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
