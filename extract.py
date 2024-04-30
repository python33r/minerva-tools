# Minerva assignment submission extractor

import re

from argparse import ArgumentParser, Namespace
from pathlib import Path
from zipfile import ZipFile

from rich.progress import track


NAME_FORMAT = re.compile(
    r"(.+)_(\w+)_attempt_(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}).(.+)"
)


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        description="Extracts assignment submissions from a Zip archive."
    )
    parser.add_argument("zipname", help="Name of Zip archive containing submissions")
    return parser.parse_args()


def extract(zipname: str) -> None:
    with ZipFile(zipname) as zfile:
        names = zfile.namelist()
        for name in track(names, description="Extracting:"):
            if match := NAME_FORMAT.match(name):
                assignment, username, _, filename = match.groups()
                dirpath = Path(assignment.lower()) / username
                dirpath.mkdir(parents=True, exist_ok=True)
                data = zfile.read(name)
                filepath = dirpath / filename
                filepath.write_bytes(data)


if __name__ == "__main__":
    args = parse_command_line()
    extract(args.zipname)
