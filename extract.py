# Minerva assignment submission extractor

import re
import sys

from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, is_zipfile

try:
    from rich.progress import track
except ImportError:
    # Allow tool to run even if Rich is unavailable
    def track(names: list, description: str) -> None:
        return names


class AssignmentExtractor:
    # regexp for the names of archive members
    NAME_FORMAT = re.compile(
        r"(.+)_(\w+)_attempt_(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}).(.+)"
    )

    def __init__(self, zpath: str, deadline: str = None) -> None:
        if not is_zipfile(zpath):
            raise FileNotFoundError(
                f"'{zpath}' does not exist or is not a valid Zip archive"
            )
        self.zip_path = zpath
        if deadline:
            self.deadline = datetime.strptime(deadline, "%Y-%m-%d:%H:%M")
        else:
            self.deadline = None
        self.late = {}

    def extract(self) -> None:
        with ZipFile(self.zip_path) as zfile:
            names = zfile.namelist()
            for name in track(names, description="Extracting:"):
                if match := self.NAME_FORMAT.match(name):
                    assignment, username, time, filename = match.groups()
                    submitted = datetime.strptime(time, "%Y-%m-%d-%H-%M-%S")
                    if self.deadline and submitted > self.deadline:
                        self.late[username] = submitted - self.deadline
                    dirpath = Path(assignment.lower()) / username
                    dirpath.mkdir(parents=True, exist_ok=True)
                    data = zfile.read(name)
                    filepath = dirpath / filename
                    filepath.write_bytes(data)

    def write_lateness(self, filename: str) -> None:
        if self.late:
            with open(filename, "wt") as outfile:
                for username, lateness in sorted(self.late.items()):
                    print(f"{username:>9s}: {lateness}", file=outfile)


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        description="Extracts assignment submissions from a Zip archive."
    )
    parser.add_argument("zip_path", help="path to Zip archive containing submissions")
    parser.add_argument(
        "--deadline", metavar="TIME", help="assignment deadline (YYYY-MM-DD:hh:mm)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_command_line()
    try:
        extractor = AssignmentExtractor(args.zip_path, args.deadline)
        extractor.extract()
        extractor.write_lateness("late.txt")
    except Exception as error:
        sys.exit(f"Error: {error}")
