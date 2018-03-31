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


def check_positive(value: str):
    """Ensures the value given is a positive number.

    :param value: A string of a number
    :return: A positive float. Raises an error if value is not positive
    """
    fvalue = float(value)
    if fvalue <= 0:
        raise argparse.ArgumentTypeError(
            "{} is an invalid positive float value".format(value))
    return fvalue


def main():
    """Generate the cli for taeper and pass args to main program."""
    parser = argparse.ArgumentParser(
        description="Simulate the real-time depositing of Nanopore "
                    "reads into a given folder, conserving the order they "
                    "were processed during sequencing. If pass and fail "
                    "folders do not exist in output_dir they will be created "
                    "if detected in the file path for the fast5 file.")

    parser.add_argument(
        "-i", "--input_dir",
        help="Directory where files are located.",
        type=str,
        required=True)

    parser.add_argument(
        "--index",
        help="Provide a prebuilt index file to skip indexing. Be aware that "
             "paths within an index file are relative to the current working "
             "directory when they were built.",
        type=str)

    parser.add_argument(
        "-o", "--output",
        help="Directory to copy the files to. If not specified, will "
             "generate the index file only.",
        type=str)

    parser.add_argument(
        "--scale",
        help="Amount to scale the timing by. i.e scale of 10 will \
                        deposit the reads 10x fatser than they were generated.\
                         (Default = 1.0)",
        type=check_positive,
        default=1.0)

    parser.add_argument(
        "-d", "--dump_index",
        help="Path to save index as. Default is 'taeper_index.npy' in current "
             "working directory. Note: Paths in the index are relative to the "
             "current working directory.",
        default='taeper_index.npy',
        type=str)

    parser.add_argument(
        "--no_index",
        help="Dont write the index list to file. This will mean it needs "
             "regenerating for this dataset on each run.",
        action='store_true'
    )

    parser.add_argument(
        "--log_level",
        help="Level of logging. 0 is none, 5 is for debugging. Default is 4 "
             "which will report info, warnings, errors, and critical "
             "information.",
        default=4,
        type=int,
        choices=range(6))

    parser.add_argument(
        "--no_progress_bar",
        help="Do not display progress bar.",
        action='store_true'
    )

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
    sys.exit(main())
