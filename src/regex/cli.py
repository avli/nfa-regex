"""A command line interface to the library.

Example usage:

.. code: console

  $ regex "a?a?b" "ab"
    The string 'ab' matches

"""
from __future__ import absolute_import, print_function
import argparse
import sys

from .executor import match
from .exceptions import MalformedRegex


def main():
    parser = argparse.ArgumentParser('Match string against regex')
    parser.add_argument('pattern', help='A POSIX-like regular expression')
    parser.add_argument('string', help='A string to match')
    args = parser.parse_args()
    try:
        m = match(args.pattern, args.string)
    except MalformedRegex:
        print("Can't parse the regular expression", file=sys.stderr)
        sys.exit(-1)
    if m:
        print("The string '%s' matches" % args.string)
        sys.exit(0)
    else:
        print("The string '%s' doesn't match" % args.string)
        sys.exit(1)


if __name__ == '__main__':
    main()