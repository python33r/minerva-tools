# Minerva assignment submission extractor

import re
import sys

from argparse import ArgumentParser, Namespace
from pathlib import Path
from zipfile import ZipFile, is_zipfile
from rich.progress import track


class AssignmentExtractor:

    # regexp for the names of archive members
    NAME_FORMAT = re.compile(
        r"(.+)_(\w+)_attempt_(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}).(.+)"
    )

    def __init__(self, zip_path) -> None:
        if not is_zipfile(zip_path):
            raise FileNotFoundError(
                f"'{zip_path}' does not exist or is not a valid Zip archive"
            )
        self.zip_path = zip_path

    def extract(self) -> None:
        with ZipFile(self.zip_path) as zfile:
            names = zfile.namelist()
            for name in track(names, description="Extracting:"):
                if match := self.NAME_FORMAT.match(name):
                    assignment, username, _, filename = match.groups()
                    dirpath = Path(assignment.lower()) / username
                    dirpath.mkdir(parents=True, exist_ok=True)
                    data = zfile.read(name)
                    filepath = dirpath / filename
                    filepath.write_bytes(data)


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        description="Extracts assignment submissions from a Zip archive."
    )
    parser.add_argument("zip_path", help="Path to Zip archive containing submissions")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_command_line()
    try:
        extractor = AssignmentExtractor(args.zip_path)
        extractor.extract()
    except Exception as error:
        sys.exit(f"Error: {error}")
