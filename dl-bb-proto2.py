"""Fetch 100 pages using httplib2."""

# Based on an eventlet recipe: 
# http://eventlet.wordpress.com/page/2/
# Actually not, I couldn't get it to work.

import os
import re
import time
import urllib

import httplib2

LATEST_PICTURES_PAGES = 100

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
