#!/usr/bin/env python
from xml.dom import minidom
import xml.sax
import timeit
import sys

def parse_using_dom(sourceFileName):
    doc = minidom.parse(sourceFileName)

    links = doc.getElementsByTagName("link")
    for link in links:
        name = link.getElementsByTagName("name")[0]
        uri = link.getElementsByTagName("uri")[0]
        print("name: %s, uri: %s" % (name.firstChild.data, uri.firstChild.data))

def parse_using_sax(sourceFileName):
    class ContentHandler(xml.sax.ContentHandler):
        def __init__(self):
            xml.sax.ContentHandler.__init__(self)

        def startElement(self, name, attrs):
            print("startElement '%s'" % name)          

        def endElement(self, name):
            print("endElement '%s'" % name)

        def characters(self, content):
            if content.strip():
                print("characters '%s'" % content)

    source = open(sourceFileName)
    xml.sax.parse(source, ContentHandler())

def make_xml():
    doc = xml.dom.minidom.Document();
    queue = doc.createElement('queue')
    link = doc.createElement('link')
    queue.appendChild(link)

    nameElement = doc.createElement('name')
    nameContent = doc.createTextNode('Paul Graham -- The Roots of Lisp')
    nameElement.appendChild(nameContent)
    nameElement.appendChild(link)
    
    doc.appendChild(queue)
    return doc


if __name__ == "__main__":
    parse_using_dom("queue.xml")
    parse_using_sax("queue.xml")

    print(timeit.timeit("parse_using_dom('queue.xml')", setup="from __main__ import parse_using_dom", number=1))
    print("Duration to parse with DOM\n\n\n")
    print(timeit.timeit("parse_using_sax('queue.xml')", setup="from __main__ import parse_using_sax", number=1))
    print("Duration to parse with SAX")

    make_xml().writexml(sys.stdout)
