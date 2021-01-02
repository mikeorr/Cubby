#!/usr/bin/env python
"""Count studz in new categories."""

import argparse
import collections
import pathlib

DEFAULT_DIR = "~/studz/new"

def get_parser():
    directory_default = pathlib.Path(DEFAULT_DIR).expanduser()
    parser = argparse.ArgumentParser()
    parser.description = __doc__.splitlines()[0]
    a = parser.add_argument
    a("directory", nargs="?", default=directory_default, type=pathlib.Path)
    return parser

def analyze_directory(d):
    results = collections.defaultdict(int)
    for p in d.iterdir():
        if p.is_dir():
            continue
        prefix = p.name.split("-")[0]
        if prefix.startswith("bdsmlr_"):
            results["bdsmlr"] += 1
        elif prefix.startswith("tumblr_"):
            results["tumblr"] += 1
        else:
            results[prefix] += 1
    return results

def print_results(results):
    indent = "    "
    for prefix, count in sorted(results.items()):
        print(f"{indent}{prefix:12s}: {count:4d}")
        #print(indent, prefix, ": ", count)

def do_directory(d):
    results = analyze_directory(d)
    print_results(results)

def main():
    parser = get_parser()
    opts = parser.parse_args()
    do_directory(opts.directory)

if __name__ == "__main__":  main()
