# Barèmes IPP

## Présentation

IPP = [Institut des politiques publiques](http://www.ipp.eu/en/)

L'IPP produit des fichiers au format XLSX appelés « Barèmes IPP » :
- en anglais : http://www.ipp.eu/en/tools/ipp-tax-and-benefit-tables/
- en français : http://www.ipp.eu/fr/outils/baremes-ipp/

Ces barèmes IPP sont très complets et il est intéressant pour OpenFisca de profiter de leur contenu.

Le script [`merge_ipp_tax_and_benefit_tables_with_parameters.py`](./merge_ipp_tax_and_benefit_tables_with_parameters.py) fusionne les barèmes IPP avec les [paramètres d'OpenFisca](../../../parameters). Le fichiers XML produits sont écrits dans ce même répertoire de paramètres.

## Utilisation

Se placer dans le répertoire racine d'OpenFisca-France, là où se trouve le fichier `setup.py`.

TODO: parler de réindenter pour séparer les commits cosmétiques.

```sh
./openfisca_france/scripts/parameters/baremes_ipp/merge_ipp_tax_and_benefit_tables_with_parameters.py -v
```

Le script prend en charge le téléchargement des fichiers YAML la première fois, et leur mise à jour ensuite.

Les fichiers [YAML clean](https://framagit.org/french-tax-and-benefit-tables/ipp-tax-and-benefit-tables-yaml-clean)  sont mis à jour par l'intégration continue côté IPP. Pour profiter de leur mise à jour, penser à faire `git pull` dans le répertoire cloné. Pour plus d'informations sur le pipeline de transformation côté IPP, voir ce [README](https://framagit.org/french-tax-and-benefit-tables/ipp-tax-and-benefit-tables-converters).

Le script produit des fichiers XML stockés dans le répertoire [`parameters`](../../../parameters). Les noms des nœuds des fichiers XML contenus dans ce répertoire cible sont identiques aux noms des paramètres contenus dans les fichiers XLS de l'IPP.

Le script utilise en entrée :
- les fichiers YAML clean de l'IPP
- [`parameters`](../../../parameters) : le répertoire de paramètres d'OpenFisca
- [`ipp_tax_and_benefit_tables_to_parameters.py`](./ipp_tax_and_benefit_tables_to_parameters.py) : définit une fonction qui :
  - renomme des paramètres provenant des barèmes IPP pour insertion dans l'arbre des paramètres OpenFisca,
  - sachant que les fichiers YAML de l'IPP contiennent uniquement des valeurs simples, crée les structures de données pour les barèmes via les fonctions `tax_scale` et `fixed_bases_tax_scale`.

Le script :
- convertit les fichiers YAML clean en représentation XML identique à celle d'OpenFisca (fonction `build_tree_from_ipp_files`),
- fusionne les 2 représentations XML, provenant d'OpenFisca et des barèmes IPP (function `merge_elements`).

## En cas de problème

Parfois le [script de fusion](#script-de-fusion) provoque une erreur.
Cela peut arriver si le script est lui-même faux, dans ce cas il s'agit d'un bug.
Mais parfois une erreur survient lorsque les données YAML en entrée ont évolué, mais pas le fichier [`ipp_tax_and_benefit_tables_to_parameters.py`](./ipp_tax_and_benefit_tables_to_parameters.py).

Exemple, à partir de cette *stack trace*:

```
Traceback (most recent call last):
  [...]
  File "./openfisca_france/scripts/parameters/baremes_ipp/merge_ipp_tax_and_benefit_tables_with_parameters.py", line 237, in main
    ipp_tax_and_benefit_tables_to_parameters.transform_ipp_tree(tree)
  File "/home/cbenz/Dev/openfisca/openfisca-france/openfisca_france/scripts/parameters/baremes_ipp/ipp_tax_and_benefit_tables_to_parameters.py", line 1063, in transform_ipp_tree
    ars['taux_primaire'] = taux_primaire = ars_m.pop('enfants_entre_6_et_11_ans_en_de_la_bmaf_1')
  [...]
KeyError: 'enfants_entre_6_et_11_ans_en_de_la_bmaf_1'
```

Explication : l'erreur réside dans la fonction `transform_ipp_tree` du module `ipp_tax_and_benefit_tables_to_parameters.py`, qui essaie à la ligne 1063 d'accéder à la clé `enfants_entre_6_et_11_ans_en_de_la_bmaf_1`. Cette clé provient d'une manière ou d'une autre des fichiers XLS de l'IPP.

Pour travailler de façon plus pratique qu'avec les fichiers XLS, nous allons chercher dans les fichiers YAML clean, qui ont été clonés précédemment dans le répertoire `ipp-tax-and-benefit-tables-yaml-clean`.

Les clés présentes dans les fichiers YAML utilisent la notation "[slug](https://en.wikipedia.org/wiki/Semantic_URL#Slug)". Partant d'une chaîne de caractères, le principe est de tout mettre en minuscules, remplacer les espaces par des `_` et retirer les caractères spéciaux.
Exemple : `Enfants entre 6 et 11 ans (En % de la BMAF) (1)` devient `enfants_entre_6_et_11_ans_en_de_la_bmaf_1`.

L'objectif est de rechercher, dans les fichiers YAML, une clé qui une fois "slugifiée" soit égale à la clé qui provoque l'erreur.

Après un peu de recherche on trouve la clé `Enfants entre 6 et 11 ans (En % de la BMAF) (1)` [ici](https://framagit.org/french-tax-and-benefit-tables/ipp-tax-and-benefit-tables-yaml-raw/commit/2b75741164aef5131b262b82fd0bcc29c016fefb#40c6be4cc89b14bd863ea81e78f9c9c300b645dc_8_5). Elle correspond bien à la version "slugifiée" `enfants_entre_6_et_11_ans_en_de_la_bmaf_1`. On voit aussi grâce au diff qu'elle a été remplacée par `Enfants entre 6 et 10 ans (En % de la BMAF) (1)`.

Pour accélérer cette recherche il est possible d'utiliser le script [`find_key_in_yaml.sh`](./find_key_in_yaml.sh).
Celui-ci va trouver dans le dépôt YAML cloné précédemment les commits contenant des clés correspondant au "slug" demandé.
Ce script est uniquement une aide à la recherche dans les logs de git.

Par exemple:
```sh
./openfisca_france/scripts/parameters/baremes_ipp/find_key_in_yaml.sh enfants_entre_11_et_15_ans_en_de_la_bmaf_2
```

Pour résoudre le problème, il faut d'abord valider d'un point de vue métier, par exemple avec un économiste, que la nouvelle clé peut être utilisée à la place de l'ancienne.

Ensuite il faut renommer effectivement la clé dans le module `ipp_tax_and_benefit_tables_to_parameters.py`, mais en utilisant la notation "slug" présentée ci-dessus.
Le script [`yaml_key_to_openfisca.py`](yaml_key_to_openfisca.py) peut être utilisé pour calculer ce "slug" :
```sh
./openfisca_france/scripts/parameters/baremes_ipp/yaml_key_to_openfisca.py "Enfants entre 6 et 10 ans (En % de la BMAF) (1)"
enfants_entre_6_et_10_ans_en_de_la_bmaf_1
```

Si on exécute à nouveau le script de fusion, l'erreur devrait disparaître, passant le cas échéant à une nouvelle erreur qui aurait lieu plus loin dans le traitement.
