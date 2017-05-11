#!/usr/bin/env bash

# Ce script aide à résoudre certaines erreurs provoquées par le script merge_ipp_tax_and_benefit_tables_with_parameters.py
# Documentation : https://github.com/openfisca/openfisca-france/tree/master/openfisca_france/scripts/parameters/baremes_ipp#script-de-fusion

SCRIPT_DIR=$(dirname $(readlink -f $BASH_SOURCE))
SCRIPT_NAME=$(basename $BASH_SOURCE)
YAML_DIR_NAME="ipp-tax-and-benefit-tables-yaml-clean"
OPENFISCA_FRANCE_DIR=$(readlink -f "$SCRIPT_DIR/../../../..")
YAML_DIR="$OPENFISCA_FRANCE_DIR/$YAML_DIR_NAME"

if [ ! -d "$YAML_DIR" ]; then
    echo "Veuillez cloner le dépôt de fichiers YAML:"
    echo "    cd $OPENFISCA_FRANCE_DIR"
    echo "    git clone https://framagit.org/french-tax-and-benefit-tables/ipp-tax-and-benefit-tables-yaml-clean.git"
    echo "Documentation : https://github.com/openfisca/openfisca-france/tree/master/openfisca_france/scripts/parameters/baremes_ipp#script-de-fusion"
    exit -1
fi

if [ -z "$1" ]; then
    echo "usage: $SCRIPT_NAME <yaml_key_as_slug>"
    exit -2
fi

YAML_KEY_AS_SLUG="$1"
YAML_KEY="^ *$(echo $YAML_KEY_AS_SLUG | sed 's/_/.+/g').*:"

cd "$YAML_DIR"
git log -p -i --pickaxe-regex -S "$YAML_KEY"
cd ..