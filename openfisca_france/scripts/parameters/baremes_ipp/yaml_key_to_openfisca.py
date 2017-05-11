#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Print a parameter name as required by OpenFisca from a YAML key as in IPP files."""


import argparse
import sys

import biryani.strings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('yaml_key', help=u"Key as in the YAML file from IPP")
    args = parser.parse_args()

    print(biryani.strings.slugify(args.yaml_key, separator=u'_'))


if __name__ == "__main__":
    sys.exit(main())
