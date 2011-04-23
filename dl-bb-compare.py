#!/usr/bin/env python
"""Compare the speed of xml.sax and BeautifulSoup on a bodybuilding.com 
latest images file.
"""

import argparse
import collections
import datetime
import logging
import os
import re
import sys
import timeit
import urlparse
import xml.sax
from xml.sax.handler import ContentHandler

from BeautifulSoup import BeautifulSoup, NavigableString, Tag

FIELD_RX = re.compile("^[A-Za-z ]+:")
BB_URL = "http://bodyspace.bodybuilding.com/"


Thumbnail = collections.namedtuple("Thumbnail", 
    ["photo_url", "thumb_url", "user_url", "username", "date"])

def get_parser():
    parser = argparse.ArgumentParser()
    paa = parser.add_argument
    paa("sample_file", action="store", metavar="SAMPLE_FILE.xhtml",
        help="Sample file to parse.")
    return parser

class BBSaxHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self.result = []

def parse_nodes_sax(html):
    handler = BBSaxHandler()
    xml.sax.parseString(html, handler)
    return handler.result

def parse_nodes_beautifulsoup(html):
    ret = []
    soup = BeautifulSoup(html)
    for node in soup.findAll("div", "boom-three-column"):
        top = node.find("div", "top")
        middle = node.find("div", "middle")
        photo_url = urlparse.urljoin(BB_URL, top.a["href"])
        thumb_url = top.img["src"]
        user_url = username = date = None
        for div in middle.findAll("div"):
            first = div.contents[0]
            if isinstance(first, NavigableString):
                if first.startswith("User:"):
                    user_url = div.a["href"]
                    username = user_url.rsplit("/", 1)[1]
                elif first.startswith("Date Taken:"):
                    fmt = "Date Taken: %b %d, %Y"
                    date = datetime.datetime.strptime(first, fmt).date()
        thumbnail = Thumbnail(photo_url=photo_url, thumb_url=thumb_url, 
            user_url=user_url, username=username, date=date)
        ret.append(thumbnail)
    return ret

def main():
    logging.basicConfig(level=logging.INFO)
    parser = get_parser()
    args = parser.parse_args()
    f = open(args.sample_file, "r")
    html = f.read()
    f.close()
    print "Initial pass with BeautifulSoup."
    nodes_bs = parse_nodes_beautifulsoup(html)
    print "Initial pass with SAX."
    nodes_sax = parse_nodes_sax(html)
    #assert nodes_bs == nodes_sax
    print "Parsing with BeautifulSoup"
    timeit.timeit("parse_nodes_beautifulsoup(html)", repeat=10, number=1)
    print "Parsing with SAX"
    timeit.timeit("parse_nodes_sax(html)", repeat=10, number=1)
        
if __name__ == "__main__":  main()
