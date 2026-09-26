"""Run this project's required tests, rejecting empty discovery."""
from pathlib import Path
import sys
import unittest


def main():
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent))
    if suite.countTestCases() == 0:
        print("ERROR: no tests discovered; required validation did not run.", file=sys.stderr)
        return 1
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
