#!/usr/bin/env python

import sys
from html.parser import HTMLParser
import re

import zipfile

class TOCParser(HTMLParser):
    def __init__(self):
        super(TOCParser, self).__init__()
        self.pages = []

    def find_attr(self, attrs, attr):
        for elm in attrs:
            if attr in elm:
                if '#' not in elm[1]:
                    return elm[1]

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = self.find_attr(attrs, 'href')
            if href:
                self.pages.append(href)

class PageParser(HTMLParser):
    def __init__(self):
        super(PageParser, self).__init__()
        self.stack_of_tags = []
        self.ignore_these_tags = ['html', 'head', 'body', 'title']
        self.output_text = []

    def handle_starttag(self, tag, attrs):
        self.stack_of_tags.append(tag)

    def handle_endtag(self, tag):
        self.stack_of_tags.pop()

    def handle_data(self, data):
        if len(self.stack_of_tags) == 0:
            return

        if self.stack_of_tags[-1] in self.ignore_these_tags:
            return

        data = data.strip()
        if len(data) == 0:
            return

        self.output_text.append(data)

    def text(self):
        return " ".join(self.output_text)

    def clear(self):
        self.stack_of_tags = []
        self.output_text = []

class EPUBParser:
    def parse(self, filename):
        zf = zipfile.ZipFile(filename)
        filenames, toc = self.get_names(zf)

        if toc == '':
          print("Failed to find the toc")
          sys.exit(1)

        pages_to_convert = self.get_used_pages(zf, toc)

        parser = PageParser()

        lines = []

        for page in pages_to_convert:
            fn = self.find(filenames, page)

            doc = ''

            with zf.open(fn) as fh:
                for line in fh:
                    doc += line.decode("utf-8")

            parser.feed(doc)
            lines.append(parser.text())
            parser.clear()

        pattern = re.compile(r'\s+')
        sentence = re.sub(pattern, ' ', " ".join(lines))

        return sentence

    def get_names(self, zf):
        filenames = []
        toc = ''

        for x in zf.infolist():
          if x.filename.endswith(".html"):
            filenames.append(x.filename)

            if x.filename.endswith("/toc.html"):
              toc = x.filename

        return filenames, toc

    def get_used_pages(self, zf, toc):
        doc = ""

        with zf.open(toc) as th:
          for line in th:
              doc += line.decode("utf-8")

        parser = TOCParser()
        parser.feed(doc)

        return parser.pages

    def find(self, filenames, name):
        for filename in filenames:
            if filename.endswith(name):
                return filename
