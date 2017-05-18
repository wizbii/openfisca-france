#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Reindent an XML file. Useful to separate cosmetic commits from real updates."""


import argparse
import sys
import lxml.etree as etree


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('file_name', help = "XML file to reindent")
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()

    tree = etree.parse(args.file_name)
    root_element = tree.getroot()
    with open(args.file_name, 'w') as xml_file:
        xml_file.write(etree.tostring(root_element, pretty_print=True, encoding='utf-8'))

    return 0


if __name__ == "__main__":
    sys.exit(main())
