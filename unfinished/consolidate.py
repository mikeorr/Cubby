"""Consolidate gaps in numbered files.
"""
import argparse

def get_argument_parser():
    parser = argparse.ArgumentParser
    paa = parser.add_argument
    paa("-m", action="store_true",
        "Don't modify files; print maximum number that would be generated.")
    paa("-n", action="store_true",
        help="Don't modify files; print what they would be renamed from and to.")
    return parser


def main():
    parser = get_argument_parser()
    args = parser.parse_args()


if __name__ == "__main__":  main()
