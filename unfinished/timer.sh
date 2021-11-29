#!/usr/bin/env python
"""A simple timer."""

import argparse
import time

def get_parser():
    parser = argparse.ArgumentParser()
    parser.description = __doc__.splitlines()[0]
    paa = parser.add_argument
    paa("minutes", type=int)
    return parser

def main():
    parser = get_parser()
    opts = parser.parse_args()
    start = time.time()
    throttle = 10.0   # Update status every N seconds.
    while True:
        now = time.time()
        remaining = start - now
        if remaining < 1.0:
            break
        print(int(remaining), "minutes remaining.")
        time.sleep(throttle)
    print("Beep!\a")

if __name__ == "__main__":  main()
