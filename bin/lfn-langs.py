#!/usr/bin/python
"""List the languages in the Elefen dictionary data.

http://elefen.org/disionario/disionario_completa.txt
"""

from __future__ import print_function
import argparse
import collections
import re

LANG_RE = re.compile(r"^\s+:([A-Z][A-Z]) ")

def get_parser():
    description = __doc__.splitlines()[0]
    parser = argparse.ArgumentParser(description=description)
    paa = parser.add_argument
    paa("file", help="Source file. (disionario_completa.txt')")
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    elements = []
    rx = re.compile(LANG_RE)
    f = open(args.file, "r")
    for lin in f:
        m = rx.match(lin)        
        if m:
            lang = m.group(1)
            elements.append(lang)
    counter = collections.Counter(elements)
    langs = counter.most_common()
    fmt = "{}: {:5d}"
    for lang, count in langs:
        print(fmt.format(lang, count))

if __name__ == "__main__":  main()
