"""Module that adds cli options to the current external_scripts."""

import argparse

from .extract_subtitle_labels.ffmpeg_export import FfmpegCsvExporter


def extract_csv_stills(args):
    """Applies the args to an instance of the FfmpegCsvExporter class.

    Args:
        args: User input argiments.
    """
    ffmpeg = FfmpegCsvExporter(args.csvs,
                               args.media,
                               args.output,
                               verbose=args.verbose,
                               log_filepath=args.log)
    ffmpeg.extract_frames()


def connect_cli():
    """Gathers individual scripts and enables cli interaction"""

    parser = argparse.ArgumentParser(
        prog="External Scripts",
        description="Additional utilities to be run outside of Resolve.",
    )
    subparsers = parser.add_subparsers(help='Scripts', dest='script')

    extract_stills = subparsers.add_parser(
        "extract_stills",
        help='Uses the csvs generated from the resolve script '
             '"extract_subtitle_labels.py" to extract still images at the '
             'indicated frames.')
    extract_stills.add_argument(
        "--csvs",
        "-c",
        help="The path to the csvs directory. Will default to the current "
             "folder if not specified.",
        metavar='DIRECTORY',
        default=".",
        type=str)
    extract_stills.add_argument(
        "--media",
        "-m",
        help="The path to the media directory. Will default to the current "
             "folder if not specified.",
        metavar='DIRECTORY',
        default=".",
        type=str)
    extract_stills.add_argument(
        "--output",
        "-o",
        help="The path to the output directory. Will default to the media "
             "folder if not specified.",
        metavar='DIRECTORY',
        type=str)
    extract_stills.add_argument(
        "--log",
        "-l",
        help="The path for the log file.",
        metavar='PATH',
        default="./extract_subtitles_labels.log",
        type=str)
    extract_stills.add_argument(
        "--verbose",
        "-v",
        help="Increases verbosity of shell messages.",
        action='store_true')

    args = parser.parse_args()

    if args.script == "extract_stills":
        extract_csv_stills(args)


def main():
    connect_cli()


if __name__ == "__main__":
    main()
