#!/usr/bin/env python

# Notes for future:
# Eventlet usage: http://eventlet.wordpress.com/page/2/

import argparse
import collections
import datetime
import logging
import os
import re
import sys
import time
import urllib
import urlparse

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
import httplib2

DOWNLOAD_PAGE_COUNT = 50
COLUMNS = 9
OUTPUT_FILE = "/tmp/bb.html"
FIELD_RX = re.compile("^[A-Za-z ]+:")
BB_URL = "http://bodyspace.bodybuilding.com/"
PICTURES_URL = "http://bodyspace.bodybuilding.com/photos/view-latest/all"
PICTURES_PER_PAGE = 18

class Timer(object):
    def __init__(self):
        self.reset()

    def checkpoint(self):
        now = time.time()
        elapsed = now - self.start
        self.start = now
        return elapsed

    def total(self):
        now = time.time()
        elapsed = now - self.total_start
        return elapsed

    def reset(self):
        now = time.time()
        self.total_start = now
        self.start = now
        

Thumbnail = collections.namedtuple("Thumbnail", 
    ["photo_url", "thumb_url", "user_url", "username", "date"])

def get_parser():
    parser = argparse.ArgumentParser()
    paa = parser.add_argument
    paa("-n", action="store", dest="nr_pages", type=int,
        default=DOWNLOAD_PAGE_COUNT, 
        help="Number of pages to fetch. (Default {0}.)".format(
            DOWNLOAD_PAGE_COUNT))
    paa("-d", action="store_true", dest="download_only",
        help="Download only (write one page to standard output).")
    paa("-r", action="store_true", dest="read",
        help="Read page from standard input instead of downloading.")
    paa("-o", action="store", dest="output",
        help="Output file (default '{0}').".format(OUTPUT_FILE))
    paa("-c", action="store", dest="columns",
        help="Number of thumbnail columns on output (default {0}).".format(
            COLUMNS))
    paa("--debug", action="store_true",
        help="Enable debug logging.")
    parser.set_defaults(nr_pages=DOWNLOAD_PAGE_COUNT, output=OUTPUT_FILE,
        columns=COLUMNS)
    return parser

def get_url(http, url, **params):
    orig_url = url
    if params:
        qs = urllib.urlencode(params)
        url = "{0}?{1}".format(url, qs)
    logging.debug("Requesting URL '%s'", url)
    return http.request(url)[1]

def parse_nodes(html):
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

def read_page_from_stdin():
    html = sys.stdin.read()
    t = Timer()
    nodes = parse_nodes(html)
    logging.info("Parsed %d pictures in %0.4f seconds.", len(nodes), t.total())
    return nodes

def download_to_stdout():
    http = httplib2.Http()
    t = Timer()
    content = get_url(http, PICTURES_URL)
    logging.info("Downloaded 1 page in %0.4f seconds.", t.total())
    sys.stdout.write(content)

def download_indexes(nr_pages):
    logging.info("Downloading %d pages.", nr_pages)
    http = httplib2.Http()
    dst_dir = "pages"
    pages_of_nodes = []
    t = Timer()
    for i in xrange(nr_pages):
        page = i + 1
        t.checkpoint()  # Ignore any intervening time.
        if page == 1:
            content = get_url(http, PICTURES_URL)
        else:
            start = (i * PICTURES_PER_PAGE) + 1
            content = get_url(http, PICTURES_URL, start=start)
        download_time = t.checkpoint()
        nodes = parse_nodes(content)
        parse_time = t.checkpoint()
        pages_of_nodes.append(nodes)
        msg = "Downloaded page %d in %0.4f seconds, parsed in %0.4f."
        logging.info(msg, page, download_time, parse_time)
    msg = "Finished %d pages in %0.4f seconds."
    logging.info(msg, len(pages_of_nodes), t.total())
    return pages_of_nodes
    

NODE_TEMPLATE = """\
<div class="entry">
    <div><a href="{0}"><img src="{1}" width="{2}" height="{3}" /></a></div>
    <div><a href="{4}">{5}</a></div>
"""

def write_output(pages_of_nodes, output_file, columns):
    cell_fmt = '<td>{0}</td>\n'.format(NODE_TEMPLATE)
    thumb_size = 150
    columns_range = range(columns)
    f = open(output_file, "w")
    f.write("""\
<!DOCTYPE html>\n<head>
<title>Latest bodybuilding.com pictures</title>
<style>
    table {empty-cells: show;} 
    td {border: solid 1px; text-align: center;}
    th {border: solid 1px; text-align: left; height: 3em;}
</style>
</head><body><table>
""")
    for page_i, nodes in enumerate(pages_of_nodes):
        page = page_i + 1
        if not nodes:
            logging.warn("page %s has no pictures", page)
            continue
        date_str = nodes[0].date.strftime("%Y-%m-%d")
        weekday_str = nodes[0].date.strftime("%A")
        f.write('<tr>\n')
        f.write('<th>Page {0}</th>\n'.format(page))
        f.write('<th>{0}</th>\n'.format(weekday_str))
        f.write('<th>{0}</td></th>\n'.format(date_str))
        f.write('</tr>\n')
        for i in range(0, len(nodes), columns):
            f.write('<tr>\n')
            for j in columns_range:
                try:
                    node = nodes[i+j]
                except IndexError:
                    pass
                else:
                    cell = cell_fmt.format(node.photo_url, node.thumb_url,
                        thumb_size, thumb_size, node.user_url, node.username)
                    f.write(cell)
            f.write('</tr>\n')
    f.write('</table></body></html>\n')
    f.close()

def main():
    logging.basicConfig(level=logging.INFO)
    parser = get_parser()
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    if args.download_only:
        download_to_stdout()
        return
    if args.read:
        pages_of_nodes = [read_page_from_stdin()]
    else:
        pages_of_nodes = download_indexes(args.nr_pages)
    write_output(pages_of_nodes, args.output, args.columns)
        
if __name__ == "__main__":  main()
