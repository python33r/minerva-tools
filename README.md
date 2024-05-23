# minerva-tools

Tools to simplify working with Minerva, the University of Leeds VLE.

## extract.py

This tool extracts submissions from the Zip archive of submitted
work generated for a Minerva Assignment. It creates a directory with
a name derived from the name of the assignment. Inside that directory
is a subdirectory for every submitting student, named using that
student's username. That subdirectory contains the files submitted
by the student (plus a file named `txt`, containing a range of
metadata concerning the submission).

Run it with

    python extract.py --help

for more information.

This tool requires Python 3.7 or newer. It doesn't require any
additional packages to run, but you'll see a nice progress bar if
you run it in an environment where the [Rich][rich] library is
installed.

[rich]: https://github.com/Textualize/rich

## students.py

This tool generates simple plain-text lists of students' names and
usernames (one sorted by name, the other by username), from a CSV file
of module enrolment data downloaded via Faculty Services.

These lists help when marking coursework submissions extracted using
`extract.py`. The latter organises submissions by username, but Gradebook
in Minerva organises them by student name. The two lists make it easier
to map from name to username and vice versa.

Run it with

    python students.py --help

for more information.
