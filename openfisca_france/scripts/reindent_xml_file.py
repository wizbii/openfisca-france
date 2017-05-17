#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Reindent XML files."""


import argparse
import logging
import os
import sys
import xml.etree.ElementTree as etree


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


# From http://stackoverflow.com/a/34324359/3548266
class CommentedTreeBuilder(etree.TreeBuilder):
    """Keep comments in XML files."""
    def __init__(self, *args, **kwargs):
        super(CommentedTreeBuilder, self).__init__(*args, **kwargs)

    def comment(self, data):
        self.start(etree.Comment, {})
        self.data(data)
        self.end(etree.Comment)


def indent(elem, level = 0):
    # cf http://effbot.org/zone/element-lib.htm
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('file_name', help = "XML file to reindent")
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)

    tree = etree.parse(args.file_name, parser = etree.XMLParser(target = CommentedTreeBuilder()))
    root_element = tree.getroot()
    indent(root_element)
    with open(args.file_name, 'w') as xml_file:
        xml_file.write(etree.tostring(root_element, encoding = 'utf-8'))

    return 0


if __name__ == "__main__":
    sys.exit(main())
