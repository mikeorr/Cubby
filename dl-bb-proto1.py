import datetime
import re
import urllib

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
import httplib2

FIELD_RX = re.compile("^[A-Za-z ]+:")

def get_page():
    h = httplib2.Http()
    url = "http://bodyspace.bodybuilding.com/photos/view-latest/all"
    status, content = h.request(url)
    f = open("page1.html", "w")
    f.write(content)
    f.close()
    return content

def main():
    #page = get_page()
    f = open("page1.html")
    html = f.read()
    f.close()
    soup = BeautifulSoup(html)
    nodes = soup.findAll("div", "boom-three-column")
    print len(nodes), "nodes"
    print
    photo_ids = []
    for i, node in enumerate(nodes):
        print "Node #{0}.".format(i)
        top = node.find("div", "top")
        middle = node.find("div", "middle")
        photo_url = top.a["href"]
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
        print "photo_url = ", photo_url
        print "thumb_url = ", thumb_url
        print "user_url = ", user_url
        print "username = ", username
        print "date = ", date
        print
        


    

if __name__ == "__main__":  main()
