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
        
if __name__ == "__main__":  main()
