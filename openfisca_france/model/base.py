# -*- coding: utf-8 -*-

from datetime import date
import functools

from openfisca_core.columns import (
    AgeCol,
    BoolCol,
    build_column,
    DateCol,
    EnumCol,
    FixedStrCol,
    FloatCol,
    IntCol,
    PeriodSizeIndependentIntCol,
    StrCol
)
columns_import = [
    'AgeCol',
    'BoolCol',
    'build_column',
    'DateCol',
    'EnumCol',
    'FixedStrCol',
    'FloatCol',
    'IntCol',
    'PeriodSizeIndependentIntCol',
    'StrCol'
]

from openfisca_core.enumerations import Enum
from openfisca_core.formulas import (
    ARITHMETIC,
    calculate_output_add,
    calculate_output_add_divide,
    calculate_output_divide,
    dated_function,
    DatedFormulaColumn,
    EntityToPersonColumn,
    last_duration_last_value,
    make_reference_formula_decorator,
    missing_value,
    PersonToEntityColumn,
    reference_input_variable,
    set_input_dispatch_by_period,
    set_input_divide_by_period,
    SimpleFormulaColumn,
    STATE,
)

from openfisca_core.base_functions import (
    requested_period_added_value,
    requested_period_default_value,
    requested_period_last_value,
)

from openfisca_core.periods import (
    MONTH,
    YEAR
)

from ..entities import entity_class_by_symbol, Familles, FoyersFiscaux, Individus, Menages

from numpy import (
    absolute as abs_,
    logical_and as and_,
    logical_not as not_,
    logical_or as or_,
    maximum as max_,
    minimum as min_,
    )

numpy_imports = [
    'abs_',
    'and_',
    'not_',
    'or_',
    'max_',
    'min_',
    ]

__all__ = [
    'ARITHMETIC',
    'calculate_output_add',
    'calculate_output_add_divide',
    'calculate_output_divide',
    'CAT',
    'CHEF',
    'CONJ',
    'CREF',
    'date',
    'dated_function',
    'DatedFormulaColumn',
    'ENFS',
    'EntityToPersonColumn',
    'Enum',
    'Familles',
    'FoyersFiscaux',
    'Individus',
    'last_duration_last_value',
    'Menages',
    'missing_value',
    'MONTH',
    'PAC1',
    'PAC2',
    'PAC3',
    'PART',
    'PersonToEntityColumn',
    'PREF',
    'QUIFAM',
    'QUIFOY',
    'QUIMEN',
    'reference_formula',
    'reference_input_variable',
    'requested_period_added_value',
    'requested_period_default_value',
    'requested_period_last_value',
    'set_input_dispatch_by_period',
    'set_input_divide_by_period',
    'SimpleFormulaColumn',
    'STATE',
    'TAUX_DE_PRIME',
    'VOUS',
    'YEAR',
    ] + numpy_imports + columns_import

CAT = Enum([
    'prive_non_cadre',
    'prive_cadre',
    'public_titulaire_etat',
    'public_titulaire_militaire',
    'public_titulaire_territoriale',
    'public_titulaire_hospitaliere',
    'public_non_titulaire',
    ])

TAUX_DE_PRIME = 1 / 4  # primes_fonction_publique (hors suppl. familial et indemnité de résidence)/rémunération brute

QUIFAM = Enum(['chef', 'part', 'enf1', 'enf2', 'enf3', 'enf4', 'enf5', 'enf6', 'enf7', 'enf8', 'enf9'])
QUIFOY = Enum(['vous', 'conj', 'pac1', 'pac2', 'pac3', 'pac4', 'pac5', 'pac6', 'pac7', 'pac8', 'pac9'])
QUIMEN = Enum(['pref', 'cref', 'enf1', 'enf2', 'enf3', 'enf4', 'enf5', 'enf6', 'enf7', 'enf8', 'enf9'])

CHEF = QUIFAM['chef']
CONJ = QUIFOY['conj']
CREF = QUIMEN['cref']
ENFS = [
    QUIFAM['enf1'], QUIFAM['enf2'], QUIFAM['enf3'], QUIFAM['enf4'], QUIFAM['enf5'], QUIFAM['enf6'], QUIFAM['enf7'],
    QUIFAM['enf8'], QUIFAM['enf9'],
    ]
PAC1 = QUIFOY['pac1']
PAC2 = QUIFOY['pac2']
PAC3 = QUIFOY['pac3']
PART = QUIFAM['part']
PREF = QUIMEN['pref']
VOUS = QUIFOY['vous']


# Functions and decorators


build_column = functools.partial(
    build_column,
    entity_class_by_symbol = entity_class_by_symbol,
    )

reference_formula = make_reference_formula_decorator(entity_class_by_symbol = entity_class_by_symbol)
