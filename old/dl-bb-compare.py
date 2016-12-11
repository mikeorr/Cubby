#!/usr/bin/env python
"""Compare the speed of lxml and BeautifulSoup on a bodybuilding.com 
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
from lxml.etree import dump
import lxml.html

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

def parse_nodes_lxml(html):
    ret = []
    tree = lxml.html.document_fromstring(html)
    for container in tree.find_class("boom-three-column"):
        top = container.find_class("top")[0]
        middle = container.find_class("middle")[0]
        photo_url = urlparse.urljoin(BB_URL, top.find("a").get("href"))
        thumb_url = top.getiterator("img").next().get("src")
        user_url = username = date = None
        for div in middle.findall("div"):
            text = div.text or ""
            if text.startswith("User:"):
                user_url = div.find("a").get("href")
                username = user_url.rsplit("/", 1)[1]
            elif text.startswith("Date Taken:"):
                fmt = "Date taken: %b %d, %Y"
                date = datetime.datetime.strptime(text, fmt).date()
        thumbnail = Thumbnail(photo_url=photo_url, thumb_url=thumb_url, 
            user_url=user_url, username=username, date=date)
        ret.append(thumbnail)
    return ret

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
    print "Initial pass with lxml."
    nodes_lxml = parse_nodes_lxml(html)
    print "Parsing with BeautifulSoup"
    def bs():
        return parse_nodes_beautifulsoup(html)
    print min(timeit.repeat(bs, repeat=10, number=1))
    print "Parsing with lxml"
    def lx():
        return parse_nodes_lxml(html)
    print min(timeit.repeat(lx, repeat=10, number=1))
        
if __name__ == "__main__":  main()
