# Barèmes IPP

## Présentation

IPP = [Institut des politiques publiques](http://www.ipp.eu/en/)

L'IPP produit des fichiers au format XLSX appelés « Barèmes IPP » :
- en anglais : http://www.ipp.eu/en/tools/ipp-tax-and-benefit-tables/
- en français : http://www.ipp.eu/fr/outils/baremes-ipp/

Ces barèmes IPP sont très complets et il est intéressant pour OpenFisca de profiter de leur contenu.

Le script [`merge_ipp_tax_and_benefit_tables_with_parameters.py`](./merge_ipp_tax_and_benefit_tables_with_parameters.py) a été créé afin de fusionner les barèmes IPP avec les paramètres d'OpenFisca ([`param.xml`](./param.xml)). Le fichiers XML produits sont écrits dans le répertoire [`parameters`](../../../parameters).

## Utilisation

Se placer dans le répertoire racine d'OpenFisca-France, là où se trouve le fichier `setup.py`.

### Script de fusion

```sh
git clone https://framagit.org/french-tax-and-benefit-tables/ipp-tax-and-benefit-tables-yaml-clean.git
./openfisca_france/scripts/parameters/baremes_ipp/merge_ipp_tax_and_benefit_tables_with_parameters.py --source-dir ipp-tax-and-benefit-tables-yaml-clean -v
```

Le script [`merge_ipp_tax_and_benefit_tables_with_parameters.py`](./merge_ipp_tax_and_benefit_tables_with_parameters.py) utilise en entrée :
- les fichiers [YAML clean](https://framagit.org/french-tax-and-benefit-tables/ipp-tax-and-benefit-tables-yaml-clean) produits par le pipeline de transformation de données exécuté côté IPP et décrit [ici](https://framagit.org/french-tax-and-benefit-tables/ipp-tax-and-benefit-tables-converters#in-the-ipp-world)
- [`param.xml`](https://github.com/openfisca/openfisca-france/blob/master/openfisca_france/scripts/parameters/baremes_ipp/param.xml) : le fichier de paramètres d'OpenFisca
- [`param-to-parameters.yaml`](https://github.com/openfisca/openfisca-france/blob/master/openfisca_france/scripts/parameters/baremes_ipp/param-to-parameters.yaml) : une table de correspondance indiquant, pour certains barèmes IPP, un nouveau nom correspondant à l'arborescence OpenFisca
- [`ipp_tax_and_benefit_tables_to_parameters.py`](https://github.com/openfisca/openfisca-france/blob/master/openfisca_france/scripts/parameters/baremes_ipp/ipp_tax_and_benefit_tables_to_parameters.py) : définit une fonction qui transforme les barèmes IPP. TODO : à documenter mieux

Le script produit des fichiers XML stockés dans le répertoire [`parameters`](https://github.com/openfisca/openfisca-france/tree/master/openfisca_france/parameters).

### Script de visualisation

```sh
./openfisca_france/scripts/parameters/baremes_ipp/show_merged_parameters.py
```
