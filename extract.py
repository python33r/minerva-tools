# Minerva assignment submission extractor

import re
import sys
import textwrap

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, is_zipfile

try:
    from rich.progress import track
except ImportError:
    # Allow tool to run even if Rich is unavailable
    def track(names: list, description: str) -> list:
        return names


DEFAULT_LATE_FILE = "late.txt"


class AssignmentExtractor:
    """
    Submission extractor for Minerva Assignments.
    """

    # regexp for the names of archive members
    NAME_FORMAT = re.compile(
        r"(.+)_(\w+)_attempt_(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}).(.+)"
    )

    SPACES = re.compile(r"\s+")

    def __init__(self, zpath: str, deadline: str = None, verbose: bool = False) -> None:
        """
        Creates an AssignmentExtractor for a Zip archive with the given path.

        The assignment deadline can optionally be specified, in YYYY-MM-DD:hh:mm
        format. If this is done, the extractor will collect information on late
        submissions as part of the extraction process.
        """
        if not is_zipfile(zpath):
            raise FileNotFoundError(
                f"'{zpath}' does not exist or is not a valid Zip archive"
            )
        self.zip_path = zpath
        if deadline:
            self.deadline = datetime.strptime(deadline, "%Y-%m-%d:%H:%M")
        else:
            self.deadline = None
        self.verbose = verbose
        self.usernames = set()
        self.late = {}

    def extract(self) -> None:
        """
        Runs the extraction process on an Assignment Zip archive.
        """
        with ZipFile(self.zip_path) as zfile:
            names = zfile.namelist()
            for name in track(names, description="Extracting:"):
                if match := self.NAME_FORMAT.match(name):
                    assignment, username, time, filename = match.groups()
                    self.usernames.add(username)

                    submitted = datetime.strptime(time, "%Y-%m-%d-%H-%M-%S")
                    if self.deadline and submitted > self.deadline:
                        self.late[username] = submitted - self.deadline

                    basedir = self.SPACES.sub("_", assignment.lower())
                    dirpath = Path(basedir) / username
                    dirpath.mkdir(parents=True, exist_ok=True)
                    filepath = dirpath / filename
                    filepath.write_bytes(zfile.read(name))

        if self.verbose:
            print()
            print(f"{len(self.usernames)} submitters processed")

    def write_lateness(self, filename: str) -> None:
        """
        Writes information on late submissions to the given file, if such
        information was collected during extraction.
        """
        if self.late:
            with open(filename, "wt") as outfile:
                for username, lateness in sorted(self.late.items()):
                    print(f"{username:>8s}: {lateness}", file=outfile)
            if self.verbose:
                print(f"{len(self.late)} late submissions")
                print(f"Lateness information written to {filename}")


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
        Extracts submissions from an Assignment Zip archive.

        A destination directory is created, named after the assignment. Within
        this directory are subdirectories, one for each student, containing that
        student's submitted files. Student usernames are used as the names
        of these subdirectories.

        If a deadline is specified, information on late submissions will be
        collected and written to a file.
        """),
    )
    parser.add_argument("zip_path", help="path to Zip archive containing submissions")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="provide more information on submission extraction",
    )
    parser.add_argument(
        "--deadline", metavar="TIME", help="assignment deadline (YYYY-MM-DD:hh:mm)"
    )
    parser.add_argument(
        "--latefile",
        default=DEFAULT_LATE_FILE,
        metavar="FILE",
        help="name of lateness file (default: %(default)s)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_command_line()
    try:
        extractor = AssignmentExtractor(args.zip_path, args.deadline, args.verbose)
        extractor.extract()
        extractor.write_lateness(args.latefile)
    except Exception as error:
        sys.exit(f"Error: {error}")
