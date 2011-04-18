"""Fetch 100 pages using httplib2."""

# Based on an eventlet recipe: 
# http://eventlet.wordpress.com/page/2/
# Actually not, I couldn't get it to work.

import argparse
import os
import re
import time
import urllib

import httplib2

LATEST_PICTURES_PAGES = 100

def get_parser():
    parser = argparse.ArgumentParser()
    paa = parser.add_argument
    paa("n", action="store", dest="pages", type=int,
        help="Number of pages to fetch.")
    paa("w", action="store", dest="write",
        help="Write pages to the specified directory.")
    paa("r", action="store", dest="read",
        help="Read pages from the specified directory. (Disables downloading.)")
    paa("output", action="store", 
        help="Output file (HTML).")
    return parser

def main():
    http = httplib2.Http()
    url = "http://bodyspace.bodybuilding.com/photos/view-latest/all"
    dst_dir = "pages"
    if not os.path.exists(dst_dir):
        os.path.makedirs(dest_dir)
    begin = time.time()
    for i in xrange(LATEST_PICTURES_PAGES):
        page = i + 1
        start = 19 * i
        qs = urllib.urlencode({"start": start})
        u = "{0}?{1}".format(url, qs)
        page_begin = time.time()
        headers, content = http.request(u)
        elapsed = time.time() - page_begin
        print "... page {0} ({1:0.4f} seconds)".format(page, elapsed)
        filename = "page-{0:03}.html".format(page)
        p = os.path.join(dst_dir, filename)
        f = open(p, "w")
        f.write(content)
        f.close()
    elapsed = time.time() - begin
    msg = "Finished {0} pages in {1:0.4f} seconds"
    print msg.format(LATEST_PICTURES_PAGES, elapsed)

if __name__ == "__main__":  main()

# 3

import collections
import datetime
import os
import re
import time
import urllib
import urlparse

from BeautifulSoup import BeautifulSoup, NavigableString, Tag

FIELD_RX = re.compile("^[A-Za-z ]+:")
bodyspace_url = "http://bodyspace.bodybuilding.com/"

Thumbnail = collections.namedtuple("Thumbnail", 
    ["photo_url", "thumb_url", "user_url", "username", "date"])

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
                    date = datetime.datetime.strptime(first, "Date Taken: %b %d, %Y").date()
        thumbnail = Thumbnail(photo_url=photo_url, thumb_url=thumb_url, 
            user_url=user_url, username=username, date=date)
        yield thumbnail

def main():
    pages_dir = "pages"
    thumbnails = []
    count = 0
    start = time.time()
    for filename in os.listdir(pages_dir):
        p = os.path.join(pages_dir, filename)
        f = open(p)
        html = f.read()
        f.close()
        for th in iter_nodes(html):
            count += 1
            thumbnails.append(th)
            print "Node #{0}".format(count)
    elapsed = time.time() - start
    print thumbnails[0]
    print len(thumbnails), "thumbnails."
    print "Finished in {0:0.4f} seconds.".format(elapsed)

def parse_files(record_dir):
    return None

def download_indexes(record_dir):
    return None

def write_output(info, output_file):
    pass

def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.read:
        info = parse_files(args.read)
    else:
        info = download_indexes(args.write)
    write_output(info, args.output)
        
if __name__ == "__main__":  main()
