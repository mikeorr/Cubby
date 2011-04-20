"""Fetch 100 pages using httplib2."""

# Notes for future:
# Eventlet usage: http://eventlet.wordpress.com/page/2/

import argparse
import collections
import datetime
import os
import re
import time
import urllib
import urlparse

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
import httplib

DEFAULT_DOWNLOAD_PAGE_COUNT = 100
LATEST_PICTURES_PAGES = 100
FIELD_RX = re.compile("^[A-Za-z ]+:")
bodyspace_url = "http://bodyspace.bodybuilding.com/"

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
        default=DEFAULT_DOWNLOAD_PAGE_COUNT, 
        help="Number of pages to fetch. (Default {0}.)".format(
            DEFAULT_DOWNLOAD_PAGE_COUNT))
    paa("-w", action="store", dest="write",
        help="Write pages to the specified directory.")
    paa("-r", action="store", dest="read",
        help="Read pages from the specified directory. (Disables downloading.)")
    paa("output", action="store", 
        help="Output file (HTML).")
    return parser

def iter_nodes(html):
    soup = BeautifulSoup(html)
    for node in soup.findAll("div", "boom-three-column"):
        top = node.find("div", "top")
        middle = node.find("div", "middle")
        photo_url = urlparse.urljoin(bodyspace_url, top.a["href"])
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
        yield thumbnail

def parse_files(record_dir):
    thumbnails = []
    count = 0
    t = Timer()
    for filename in os.listdir(record_dir):
        p = os.path.join(record_dir, filename)
        f = open(p)
        html = f.read()
        f.close()
        for th in iter_nodes(html):
            count += 1
            thumbnails.append(th)
            print "Node #{0}".format(count)
    print len(thumbnails), "thumbnails."
    print "Finished in {0:0.4f} seconds.".format(t.total())
    return thumbnails

def download_indexes(record_dir, nr_pages):
    http = httplib2.Http()
    url = "http://bodyspace.bodybuilding.com/photos/view-latest/all"
    dst_dir = "pages"
    if record_dir and not os.path.exists(record_dir):
        os.makedirs(record_dir)
    nodes = []
    t = Timer()
    for i in xrange(nr_pages):
        page = i + 1
        start = 19 * i
        qs = urllib.urlencode({"start": start})
        u = "{0}?{1}".format(url, qs)
        t.checkpoint()  # Ignore any intervening time.
        headers, content = http.request(u)
        download_time = t.checkpoint()
        nodes.extend(iter_nodes(content))
        parse_time = t.checkpoint()
        if record_dir:
            filename = "page-{0:03}.html".format(page)
            p = os.path.join(record_dir, filename)
            f = open(p, "w")
            f.write(content)
            f.close()
        msg = "... page {0} ({1:0.4f} seconds to download, {2:0.4f} to parse))"
        print msg.format(page, download_time, parse_time)
    msg = "Finished {0} pages in {1:0.4f} seconds"
    print msg.format(nr_pages, t.total())
    return nodes


NODE_TEMPLATE = """\
<div class="entry">
    <div><a href="{0}"><img src="{1}" width="{2}" height="{3}" /></a></div>
    <div><a href="{4}">{5}</a></div>
"""

def write_output(nodes, output_file):
    cell_fmt = '<td>{0}</td>\n'.format(NODE_TEMPLATE)
    thumb_size = 150
    columns = 11
    f = open(output_file, "w")
    f.write('<!DOCTYPE html>\n<head>\n')
    f.write('<style>table {} td {border: solid 1px;}</style>\n')
    f.write('</head><body><table>\n')
    columns_range = range(columns)
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
    parser = get_parser()
    args = parser.parse_args()
    if args.read:
        info = parse_files(args.read)
    else:
        info = download_indexes(args.write, args.nr_pages)
    write_output(info, args.output)
        
if __name__ == "__main__":  main()
