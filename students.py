# Student name & username list generator

import csv
import textwrap

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter


type StudentRecord = tuple[str, str]
type StudentList = list[StudentRecord]


def get_student_details(csvpath: str) -> StudentList:
    """
    Extracts student names & usernames from a module enrolment CSV file.
    """
    details = []
    with open(csvpath, "rt") as infile:
        reader = csv.DictReader(infile)
        for record in reader:
            name = record["Student Name"].strip()
            username, _ = record["Email Address"].split("@")
            details.append((username, name))
    return details


def write_list(data: StudentList, filename: str, numbered: bool = False) -> None:
    """
    Writes student usernames & names to the given text file.
    """
    with open(filename, "wt") as outfile:
        for index, item in enumerate(data):
            username, name = item
            if numbered:
                print(f"{index+1:3d}  {username:8s}  {name}", file=outfile)
            else:
                print(f"{username:8s}  {name}", file=outfile)


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
        Creates lists of student names & usernames from a module enrolment file.

        The module enrolment file is the standard CSV file downloaded via
        Faculty Services.

        The tool outputs two lists: one sorted by student name, the other sorted
        by username. List entries can optionally be numbered.

        The lists can be used to map from name to username and vice versa,
        reconciling the 'by username' organisation of downloaded coursework and
        the 'by name' listing used by Gradebook in Minerva.
        """),
    )
    parser.add_argument("csv_path", help="path to module enrolment CSV file")
    parser.add_argument("names_path", help="path to 'sorted by name' list")
    parser.add_argument("usernames_path", help="path to 'sorted by username' list")
    parser.add_argument(
        "-n",
        "--numbered",
        action="store_true",
        default=False,
        help="add line numbers to both output files",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_command_line()
    details = get_student_details(args.csv_path)
    write_list(details, args.names_path, args.numbered)
    write_list(sorted(details), args.usernames_path, args.numbered)
