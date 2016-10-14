#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Import a parameter of the legislation from [G6K](https://gitlab.com/pidila/sp-simulateurs-data).
"""


import argparse
import json
import logging
import os
import sys
import xml.etree.ElementTree as etree


# Globals


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)

transformation_data_by_g6k_name = {
    'plafondHoraire': {
        'openfisca_parameter_path': ['cotsoc', 'gen', 'plafond_securite_sociale_horaire'],
        'value_key_name': 'plafond',
        },
    'TauxMinimal': {
        'openfisca_parameter_path': ['stage', 'taux_gratification_min'],
        'value_key_name': 'taux',
        },
    }


def g6k_parameter_to_code_element(g6k_name, g6k_parameter):
    global transformation_data_by_g6k_name
    transformation_data = transformation_data_by_g6k_name[g6k_name]
    code_element = etree.Element('CODE', attrib={
        'code': transformation_data['openfisca_parameter_path'][-1],
        'origin': u'g6k',
        })
    for period_dict in g6k_parameter:
        value_element = etree.Element('VALUE', attrib={
            'deb': period_dict['debutPeriode'],
            'fin': period_dict['finPeriode'],
            'valeur': unicode(period_dict[transformation_data['value_key_name']]),
            })
        code_element.append(value_element)
    return code_element


def reindent(elem, depth = 0):
    # cf http://effbot.org/zone/element-lib.htm
    indent = "\n" + depth * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for elem in elem:
            reindent(elem, depth + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
    else:
        if depth and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


def find_parameter_element(root, path):
    xpath = './[code="root"]/' + (
        '/'.join('[code="{}"]'.format(fragment) for fragment in path)
        )
    element = root.find(xpath)
    return element


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('input_json_file_path', help=u'Input JSON file')
    parser.add_argument('xml_parameters_file_path', help=u'Input and output XML file')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help=u'Increase output verbosity')
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)

    with open(args.input_json_file_path) as input_json_file:
        input_json = json.load(input_json_file)

    xml_parameters_tree = etree.parse(args.xml_parameters_file_path)

    for g6k_name, g6k_parameter in input_json.items():
        g6k_code_element = g6k_parameter_to_code_element(g6k_name, g6k_parameter)
        transformation_data = transformation_data_by_g6k_name[g6k_name]
        path = transformation_data['openfisca_parameter_path']
        original_code_element = find_parameter_element(xml_parameters_tree, path)
        reindent(g6k_code_element)
        print(etree.tostring(g6k_code_element))

    return 0


if __name__ == '__main__':
    sys.exit(main())
