#!/usr/bin/env python

import argparse
import fnmatch
import os
import re

FILE_RX = re.compile( r"^(.*?)(\d+)([a-z]?)$")
EXTENSION_RENAMES = {".jpeg": ".jpg"}

def get_parser():
    parser = argparse.ArgumentParser()
    paa = parser.add_argument
    paa("-d", dest="digits", type=int, default=3, help="Number of digits.")
    paa("-n", dest="not_really", action="store_true", help="Don't really rename files.")
    paa("-s", dest="start", type=int, default=1, help="Start number.")
    paa("-p", dest="prefix", help="Prefix.")
    paa("directory", default=".", help="Directory.")
    return parser

def main():
    parser = get_parser()
    opts = parser.parse_args()
    pattern = opts.prefix + "*"
    filenames = os.listdir(opts.directory)
    filenames = fnmatch.filter(filenames, pattern)
    filenames.sort()
    renames = []
    seq = opts.start
    stem_fmt = "{}{:0{}}{}{}"
    for filename in filenames:
        filename2 = filename
        stem, ext = os.path.splitext(filename)
        ext2 = ext
        ext2 = ext.lower()
        ext2 = EXTENSION_RENAMES.get(ext2, ext2)
        m = FILE_RX.match(stem)
        unique = False
        if m:
            while not unique:
                    prefix = m.group(1)
                    number = int(m.group(2), 10)
                    suffix = m.group(3) or ""
                    if number < seq:
                        number = seq
                    filename2 = stem_fmt.format(prefix, number, opts.digits, suffix, ext)
                    dst = os.path.join(opts.directory, filename2)
                    if os.path.exists(dst):
                        seq += 1
                        continue
                    else:
                        unique = True
                    if seq < opts.start:
                        seq = number + 1
                    else:
                        seq = seq + 1
        elif ext2:
            filename2 = stem + ext2
        #print((filename, filename2, m.groups() if m else None, seq, stem, renames))
        #import pdb; pdb.set_trace()
        if filename2 != filename:
            renames.append((filename, filename2))
    if opts.not_really:
        print("I would rename:")
    for src, dst in renames:
        src = os.path.join(opts.directory, src)
        dst = os.path.join(opts.directory, dst)
        if opts.not_really:
            print(src, "->", dst)
        else:
            print("Renaming", src, "->", dst)
            if os.path.exists(dst):
                raise FileExistsError(dst)
            else:
                os.rename(src, dst)

if __name__ == "__main__":  main()

        

