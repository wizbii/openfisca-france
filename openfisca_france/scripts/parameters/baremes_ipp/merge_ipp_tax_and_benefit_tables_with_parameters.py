#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Merge YAML files of IPP tax and benefit tables with OpenFisca parameters to generate new parameters."""


import argparse
import collections
import datetime
import itertools
import logging
import os
import subprocess
import sys
import types
import xml.etree.ElementTree as etree

from biryani import strings
from biryani.baseconv import check
from openfisca_core import legislationsxml
import yaml

from openfisca_france.france_taxbenefitsystem import FranceTaxBenefitSystem
from openfisca_france.scripts.parameters.baremes_ipp.ipp_tax_and_benefit_tables_to_parameters import transform_ipp_tree


app_name = os.path.splitext(os.path.basename(__file__))[0]
date_names = (
    # u"Age de départ (AAD=Age d'annulation de la décôte)",
    u"Date",
    u"Date d'effet",
    u"Date de perception du salaire",
    u"Date ISF",
    )
file_system_encoding = sys.getfilesystemencoding()
france_tax_benefit_system = FranceTaxBenefitSystem()
log = logging.getLogger(app_name)
note_names = (
    u"Notes",
    u"Notes bis",
    )
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
package_dir = os.path.normpath(os.path.join(script_dir, '..', '..', '..'))
parameters_dir = os.path.join(package_dir, 'parameters')
default_yaml_dir = os.path.normpath(os.path.join(package_dir, '..', 'ipp-tax-and-benefit-tables-yaml-clean'))
reference_names = (
    u"Parution au JO",
    u"Références BOI",
    u"Références législatives",
    u"Références législatives - définition des ressources et plafonds",
    u"Références législatives - revalorisation des plafonds",
    u"Références législatives des règles de calcul et du paramètre Po",
    u"Références législatives de tous les autres paramètres",
    )


def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))


yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, dict_constructor)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ipp-translations',
        default = os.path.join(script_dir, 'ipp-tax-and-benefit-tables-to-parameters.yaml'),
        help = 'path of YAML file containing the association between IPP fields and OpenFisca parameters')
    parser.add_argument('--yaml-dir', default = default_yaml_dir,
        help = 'path of directory containing clean IPP YAML files')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)

    if os.path.isdir(args.yaml_dir):
        log.info(u'Updating YAML files from IPP...')
        command = u'; '.join([
            u'cd {}'.format(args.yaml_dir),
            u'git pull',
            ])
    else:
        log.info(u'Downloading YAML files from IPP...')
        command = u'git clone {} {}'.format(
            u'https://framagit.org/french-tax-and-benefit-tables/ipp-tax-and-benefit-tables-yaml-clean.git',
            args.yaml_dir,
            )
    log.debug(command)
    subprocess.check_call(command, shell=True)

    openfisca_root_element = build_element_from_openfisca_files()

    ipp_tree = build_tree_from_ipp_files(args.yaml_dir)
    transform_ipp_tree(ipp_tree)  # User-written transformations which modify `ipp_tree`.
    ipp_root_element = transform_node_to_element(u'root', ipp_tree)

    merge_elements(openfisca_root_element, ipp_root_element)

    def write_xml_file(file_name, element):
        element_tree = etree.ElementTree(element)
        reindent(element)
        element_tree.write(
            os.path.join(parameters_dir, file_name),
            encoding = 'utf-8',
            )

    for child_element in openfisca_root_element[:]:
        write_xml_file('{}.xml'.format(child_element.attrib['code']), child_element)
        openfisca_root_element.remove(child_element)
    write_xml_file('__root__.xml', openfisca_root_element)

    return 0


def build_tree_from_ipp_files(yaml_dir):
    tree = collections.OrderedDict()
    for yaml_dir_encoded, _, filenames_encoded in os.walk(yaml_dir):
        for filename_encoded in sorted(filenames_encoded):
            if not filename_encoded.endswith('.yaml'):
                continue
            filename = filename_encoded.decode(file_system_encoding)
            sheet_name = os.path.splitext(filename)[0]
            yaml_file_path_encoded = os.path.join(yaml_dir_encoded, filename_encoded)
            relative_file_path_encoded = yaml_file_path_encoded[len(yaml_dir):].lstrip(os.sep)
            relative_file_path = relative_file_path_encoded.decode(file_system_encoding)
            if sheet_name.isupper():
                continue
            assert sheet_name.islower(), sheet_name
            log.info(u'Loading file {}'.format(relative_file_path))
            with open(yaml_file_path_encoded) as yaml_file:
                data = yaml.load(yaml_file)
            rows = data.get(u"Valeurs")
            if rows is None:
                log.info(u'  Skipping file {} without "Valeurs"'.format(relative_file_path))
                continue
            row_by_start = {}
            for row in rows:
                start = row.get(u"Date d'effet")
                if start is None:
                    for date_name in date_names:
                        start = row.get(date_name)
                        if start is not None:
                            break
                    else:
                        # No date found. Skip row.
                        continue
                elif not isinstance(start, datetime.date):
                    start = start[u"Année Revenus"]
                row_by_start[start] = row
            sorted_row_by_start = sorted(row_by_start.iteritems())

            relative_ipp_paths_by_start = {}
            unsorted_relative_ipp_paths = set()
            for start, row in sorted_row_by_start:
                relative_ipp_paths_by_start[start] = start_relative_ipp_paths = []
                for name, child in row.iteritems():
                    if name in date_names:
                        continue
                    if name in note_names:
                        continue
                    if name in reference_names:
                        continue
                    start_relative_ipp_paths.extend(
                        (name,) + tuple(path)
                        for path, value in iter_ipp_values(child)
                        )
                unsorted_relative_ipp_paths.update(start_relative_ipp_paths)

            def compare_relative_ipp_paths(x, y):
                if x == y:
                    return 0
                for relative_ipp_paths in relative_ipp_paths_by_start.itervalues():
                    try:
                        return cmp(relative_ipp_paths.index(x), relative_ipp_paths.index(y))
                    except ValueError:
                        # Either x or y paths are missing in relative_ipp_paths => Their order can't be compared.
                        continue
                return -1

            sorted_relative_ipp_paths = sorted(unsorted_relative_ipp_paths, cmp = compare_relative_ipp_paths)
            # tax_rate_tree_by_bracket_type = {}

            for start, row in sorted_row_by_start:
                for relative_ipp_path in sorted_relative_ipp_paths:
                    value = row
                    for fragment in relative_ipp_path:
                        value = value.get(fragment)
                        if value is None:
                            break

                    if value in (u'-', u'na', u'nc'):
                        # Value is unknown. Previous value must be propagated.
                        continue
                    ipp_path = [
                        fragment if fragment in ('RENAME', 'TRANCHE', 'TYPE') else strings.slugify(fragment,
                            separator = u'_')
                        for fragment in itertools.chain(
                            relative_file_path.split(os.sep)[:-1],
                            [sheet_name],
                            relative_ipp_path,
                            )
                        ]

                    sub_tree = tree
                    for fragment in ipp_path[:-1]:
                        sub_tree = sub_tree.setdefault(fragment, collections.OrderedDict())
                    fragment = ipp_path[-1]
                    sub_tree = sub_tree.setdefault(fragment, [])
                    if sub_tree:
                        previous_leaf = sub_tree[-1]
                        if previous_leaf['value'] == value:
                            # Merge leaves with the same value.
                            # One day, when we'll support "Références législatives", this behavior may change.
                            continue
                    sub_tree.append(dict(
                        start = start,
                        value = value,
                        ))
    return tree


def build_element_from_openfisca_files():
    converter = legislationsxml.make_xml_legislation_info_list_to_xml_element(with_source_file_infos = False)
    root_element = check(converter(france_tax_benefit_system.legislation_xml_info_list))
    return root_element


def iter_ipp_values(node):
    if isinstance(node, dict):
        for name, child in node.iteritems():
            for path, value in iter_ipp_values(child):
                yield [name] + path, value
    else:
        yield [], node


def merge_elements(openfisca_element, element, path = []):
    """
    Merge `element` in `openfisca_element`, modifying `openfisca_element`, only
    if each <VALUE> of `openfisca_element` is in `element` (same deb and valeur attributes),
    and if `openfisca_element` has a <END> child element, there is no corresponding <VALUE> in `element`.

    The source of truth is `openfisca_element`.

    Returns `None`.
    """
    def error_at_path(error):
        path_with_code = path + [openfisca_element.attrib['code']]
        return u'At {}: {}'.format('.'.join(path_with_code), error)

    def different_attributes_error(attribute):
        return u'{!r} attribute differs: OpenFisca={!r} and IPP={!r}'.format(
            attribute, openfisca_element.get(attribute), element.get(attribute))

    def skip_merge_error(error):
        return u'{} => skip merge for these <{}> elements'.format(error, openfisca_element.tag)

    # def show():
    #     """For debugging purpose"""
    #     print(error_at_path(""))
    #     reindent(openfisca_element)
    #     print("openfisca_element")
    #     print(etree.tostring(openfisca_element))
    #     reindent(element)
    #     print("element")
    #     print(etree.tostring(element))

    assert element.attrib['code'] == openfisca_element.attrib['code'], (element, openfisca_element)
    assert element.tag == openfisca_element.tag, \
        error_at_path(u'OpenFisca element {!r} differs from IPP element {!r}'.format(
            openfisca_element.tag, element.tag).encode('utf-8'))

    if openfisca_element.tag == 'NODE':
        for openfisca_child_element in without_comments(openfisca_element):
            for child_element in element:
                if child_element.attrib['code'] == openfisca_child_element.attrib['code']:
                    merge_elements(openfisca_child_element, child_element, path + [openfisca_element.attrib['code']])
                    break

    elif openfisca_element.tag == 'CODE':
        if openfisca_element.get('type') != element.get('type'):
            log.error(error_at_path(skip_merge_error(different_attributes_error('type'))))
            return
        # Skip merge for this openfisca_element if <END> and <PLACEHOLDER> elements in OpenFisca
        # conflict with any IPP child having the same "deb" attribute.
        for openfisca_other_element in filter(lambda child: child.tag != 'VALUE', without_comments(openfisca_element)):
            assert openfisca_other_element.tag in ['END', 'PLACEHOLDER'], openfisca_other_element.tag
            deb = openfisca_other_element.attrib['deb']
            ipp_value_element = find_child('VALUE', {'deb': deb}, element)
            if ipp_value_element is not None:
                log.error(error_at_path(skip_merge_error(
                    u'an IPP element has the same deb={!r} attribute than OpenFisca {!r} element'.format(
                        deb, openfisca_other_element.tag))))
                return
        # Remove <VALUE> elements from IPP which are both in OpenFisca and IPP.
        for openfisca_value_element in value_children(openfisca_element):
            assert openfisca_value_element.get('deb') is not None
            assert openfisca_value_element.get('valeur') is not None
            ipp_value_element = find_child(
                tag = 'VALUE',
                attributes = {
                    'deb': openfisca_value_element.attrib['deb'],
                    'valeur': openfisca_value_element.attrib['valeur'],
                    },
                element = element,
                )
            if ipp_value_element is None:
                log.error(error_at_path(skip_merge_error(
                    u'OpenFisca {!r} element was not found in IPP element children'.format(
                        etree.tostring(openfisca_value_element)))))
                return
            element.remove(ipp_value_element)
        # Add new <VALUE> elements from IPP to OpenFisca <CODE>.
        for ipp_value_element in value_children(element):
            openfisca_element.append(ipp_value_element)
            element.remove(ipp_value_element)
        assert len(element) == 0, etree.tostring(element)

    elif openfisca_element.tag == 'BAREME':
        return
        # # Some BAREME in XML files have a first TRANCHE with only zero values for TAUX and SEUIL.
        # # Skip it to ease conflict detection.
        # def only_zero_values(element):
        #     return all(
        #         float(value_element.attrib['valeur']) == 0
        #         for value_element in value_children(element)
        #         )
        # first_tranche = openfisca_element[0]
        # is_first_tranche_empty = only_zero_values(first_tranche.find('TAUX')) and \
        #     only_zero_values(first_tranche.find('SEUIL'))
        # if is_first_tranche_empty:
        #     openfisca_element = openfisca_element[1:]

        # # Check that every `openfisca_element` child (VALUE elements) is included in `element` children
        # # for each TAUX and SEUIL of each TRANCHE.
        # if len(openfisca_element) != len(element):
        #     log_error_at_path(u'Different number of <TRANCHE> elements')
        # # else:
        # #     for tranche_index, openfisca_tranche_element in enumerate(openfisca_element):
        # #         def handle_child(tag):
        # #             tag_conflicts = get_conflicts_for_values(openfisca_tranche_element.find(tag))

        # #         tranche_element = element[tranche_index]
        # #         handle_child('TAUX')
        # #         handle_child('SEUIL')
    else:
        raise NotImplementedError(openfisca_element.tag)


def prepare_xml_values(name, leafs):
    leafs = list(reversed([
        leaf
        for leaf in leafs
        if leaf['value'] is not None
        ]))
    format = None
    type = None
    for leaf in leafs:
        value = leaf['value']
        if isinstance(value, basestring):
            split_value = value.split()
            if len(split_value) == 2 and split_value[1] in (
                    u'%',
                    u'AF',  # anciens francs
                    u'CFA',  # francs CFA
                    # u'COTISATIONS',
                    u'EUR',
                    u'FRF',
                    ):
                value = float(split_value[0])
                unit = split_value[1]
                if unit == u'%':
                    if format is None:
                        format = u'percent'
                    elif format != u'percent':
                        log.warning(u'Non constant percent format {} in {}: {}'.format(format, name, leafs))
                        return None, format, type
                    value = value / 100
                else:
                    if format is None:
                        format = u'float'
                    elif format != u'float':
                        log.warning(u'Non constant float format {} in {}: {}'.format(format, name, leafs))
                        return None, format, type
                    if type is None:
                        type = u'monetary'
                    elif type != u'monetary':
                        log.warning(u'Non constant monetary type {} in {}: {}'.format(type, name, leafs))
                        return None, format, type
                    else:
                        assert type == u'monetary', type
                # elif unit == u'AF':
                #     # Convert "anciens francs" to €.
                #     value = round(value / (100 * 6.55957), 2)
                # elif unit == u'FRF':
                #     # Convert "nouveaux francs" to €.
                #     if month < year_1960:
                #         value /= 100
                #     value = round(value / 6.55957, 2)
        if isinstance(value, float) and value == int(value):
            value = int(value)
        leaf['value'] = value
    return leafs, format, type


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


def transform_node_to_element(name, node):
    """
    A `node` is a dict or a list produced by `build_tree_from_ipp_files` or `transform_ipp_tree`.
    """
    if isinstance(node, dict):
        if node.get('TYPE') == u'BAREME':
            scale_element = etree.Element('BAREME', attrib = dict(
                code = strings.slugify(name, separator = u'_'),
                origin = u'ipp',
                ))
            for slice_name in node.get('SEUIL', {}).keys():
                slice_element = etree.Element('TRANCHE', attrib = dict(
                    code = strings.slugify(slice_name, separator = u'_'),
                    ))

                threshold_element = etree.Element('SEUIL')
                values, format, type = prepare_xml_values(name, node.get('SEUIL', {}).get(slice_name, []))
                transform_values_to_element_children(values, threshold_element)
                if len(threshold_element) > 0:
                    slice_element.append(threshold_element)

                amount_element = etree.Element('MONTANT')
                values, format, type = prepare_xml_values(name, node.get('MONTANT', {}).get(slice_name, []))
                transform_values_to_element_children(values, amount_element)
                if len(amount_element) > 0:
                    slice_element.append(amount_element)

                rate_element = etree.Element('TAUX')
                values, format, type = prepare_xml_values(name, node.get('TAUX', {}).get(slice_name, []))
                transform_values_to_element_children(values, rate_element)
                if len(rate_element) > 0:
                    slice_element.append(rate_element)

                base_element = etree.Element('ASSIETTE')
                values, format, type = prepare_xml_values(name, node.get('ASSIETTE', {}).get(slice_name, []))
                transform_values_to_element_children(values, base_element)
                if len(base_element) > 0:
                    slice_element.append(base_element)

                if len(slice_element) > 0:
                    scale_element.append(slice_element)
            return scale_element if len(scale_element) > 0 else None
        else:
            node_element = etree.Element('NODE', attrib = dict(
                code = strings.slugify(name, separator = u'_'),
                origin = u'ipp',
                ))
            for key, value in node.iteritems():
                child_element = transform_node_to_element(key, value)
                if child_element is not None:
                    node_element.append(child_element)
            return node_element if len(node_element) > 0 else None
    else:
        assert isinstance(node, list), node
        values, format, type = prepare_xml_values(name, node)
        if not values:
            return None
        code_element = etree.Element('CODE', attrib = dict(
            code = strings.slugify(name, separator = u'_'),
            origin = u'ipp',
            ))
        if format is not None:
            code_element.set('format', format)
        if type is not None:
            code_element.set('type', type)
        transform_values_to_element_children(values, code_element)
        return code_element if len(code_element) > 0 else None


def transform_values_to_element_children(values, element):
    element.extend(map(
        lambda value: etree.Element('VALUE', attrib = dict(
            deb = value['start'].isoformat(),
            valeur = unicode(value['value']),
            )),
        values,
        ))


def find_child(tag, attributes, element):
    """
    Find an XML element among the children of `element`, given its `tag` and `attributes`.

    Expects zero or one result exactly.
    """
    matches = filter(
        lambda child: child.tag == tag and all(
            child.get(name) == value
            for name, value in attributes.iteritems()
            ),
        element,
        )
    assert len(matches) <= 1, matches
    return matches[0] if matches else None


def value_children(element):
    """Ignore <END> and <PLACEHOLDER> elements which are not handled by IPP YAML files."""
    return filter(lambda child: child.tag == 'VALUE', without_comments(element))


def without_comments(element):
    """Return children of `element` ignoring XML comments."""
    return filter(
        lambda child: not (isinstance(child.tag, types.FunctionType) and child.tag.__name__ == 'Comment'),
        element,
        )


if __name__ == "__main__":
    sys.exit(main())
