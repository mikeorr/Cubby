#!/usr/bin/env python

import argparse
import pathlib

def get_parser():
    parser = argparse.ArgumentParser()
    a = parser.add_argument
    a("directory", type=pathlib.Path)
    a("prefix")
    return parser

def main():
    parser = get_parser()
    opts = parser.parse_args()
    for i in range(0, 10):
        hundred = f"{opts.prefix}{i}"
        pattern = hundred + "*" 
        files = opts.directory.glob(pattern)
        count = len(tuple(files))
        print(f"{hundred}: {count:3d}")

if __name__ == "__main__": main()
