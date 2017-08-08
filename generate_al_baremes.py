import xml.etree.ElementTree as etree
import itertools

xml_file = '/repos/openfisca-france/openfisca_france/parameters/prestations.xml'
output_xml_file = '/repos/openfisca-france/openfisca_france/parameters/prestations - copie.xml'
tree = etree.parse(xml_file)
parent_node = tree.find(".//NODE[@code='al_param']") # finds the first occurrence of element tag-Name

if not len(parent_node.find('.//BAREME')):
    seuils_node = parent_node.find(".//NODE[@code='seuils']")
    taux_node = parent_node.find(".//NODE[@code='taux_pour_le_loyer_minimum_lo_en_al_accession']")

    bareme_node = etree.SubElement(parent_node, 'BAREME', { 'code': 'bareme' })

    zero_seuil = etree.SubElement(parent_node, 'SEUIL', { 'code': '1ere_tranche'})
    etree.SubElement(zero_seuil, 'VALUE', { 'deb': '1900-01-01', 'valeur': '0'})

    for (seuil, taux) in zip(itertools.chain([zero_seuil], seuils_node), taux_node):
        tranche_node = etree.SubElement(bareme_node, 'TRANCHE', { "code": taux.attrib['code'] })
        etree.SubElement(tranche_node, 'SEUIL').extend(seuil)
        etree.SubElement(tranche_node, 'TAUX').extend(taux)

    parent_node.remove(zero_seuil)


parameter_n_node = parent_node.find(".//NODE[@code='parametre_n']")
for famille_composition_node in parameter_n_node:
    if famille_composition_node.attrib['code'][0] in '1234':
        famille_composition_node.attrib['code'] = 'avec_' + famille_composition_node.attrib['code']

parent_node = tree.find(".//NODE[@code='al_param_accapl']") # finds the first occurrence of element tag-Name

if not len(parent_node.find('.//BAREME')):
    seuils_node = parent_node.find(".//NODE[@code='seuils_de_revenus']")
    taux_node = parent_node.find(".//NODE[@code='taux_pour_le_loyer_minimum_lo_pour_l_apl_accession']")

    bareme_node = etree.SubElement(parent_node, 'BAREME', { 'code': 'bareme' })

    zero_seuil = etree.SubElement(parent_node, 'SEUIL', { 'code': '1ere_tranche'})
    etree.SubElement(zero_seuil, 'VALUE', { 'deb': '1900-01-01', 'valeur': '0'})

    for (seuil, taux) in zip(itertools.chain([zero_seuil], seuils_node), taux_node):
        tranche_node = etree.SubElement(bareme_node, 'TRANCHE', { "code": taux.attrib['code'] })
        etree.SubElement(tranche_node, 'SEUIL').extend(seuil)
        etree.SubElement(tranche_node, 'TAUX').extend(taux)

    parent_node.remove(zero_seuil)



#tree.write(output_xml_file, encoding='utf-8')
tree.write(xml_file, encoding='utf-8')