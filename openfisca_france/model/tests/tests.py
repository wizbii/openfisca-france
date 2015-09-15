# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014, 2015 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from ..base import *  # noqa analysis:ignore

reference_input_variable(
    column = FloatCol,
    entity_class = Individus,
    label = u"salaire",
    name = 'test_salaire',
    category = ARITHMETIC,
    period_unit = MONTH
    )

reference_input_variable(
    column = BoolCol,
    entity_class = Individus,
    name = 'test_resident_paris',
    label =u'Résident à Paris',
    category = STATE,
    period_unit = MONTH
    )

# Formules pour tester l'ajout des formules arithmétiques

@reference_formula
class test_revenus(SimpleFormulaColumn):
    column = FloatCol
    label = u"Revenus"
    entity_class = Individus
    period_unit = YEAR
    category = ARITHMETIC


    def function(self, simulation, period):
        salaire = simulation.calculate('test_salaire', period.this_year)
        return  salaire

@reference_formula
class test_division_illegale(SimpleFormulaColumn):
    column = FloatCol
    label = u"Revenus - division illégale"
    entity_class = Individus
    period_unit = MONTH
    category = ARITHMETIC

    def function(self, simulation, period):
        revenus = simulation.calculate('test_revenus', period.this_month)
        return revenus

@reference_formula
class test_division_legale(SimpleFormulaColumn):
    column = FloatCol
    label = u"Revenus - division légale"
    entity_class = Individus
    period_unit = MONTH
    category = ARITHMETIC

    def function(self, simulation, period):
        revenus = simulation.calculate_divide('test_revenus', period.this_month)
        return revenus


@reference_formula
class test_calculate_divide_illegal(SimpleFormulaColumn):
    column = FloatCol
    label = u"Revenus - test add divide"
    entity_class = Individus
    period_unit = MONTH
    category = ARITHMETIC

    def function(self, simulation, period):
        # import ipdb
        # ipdb.set_trace()
        revenus = simulation.calculate_divide('test_revenus', period.last_3_months)
        return revenus

@reference_formula
class test_add_divide(SimpleFormulaColumn):
    column = FloatCol
    label = u"Revenus - test add divide"
    entity_class = Individus
    period_unit = MONTH
    category = ARITHMETIC

    def function(self, simulation, period):
        # import ipdb
        # ipdb.set_trace()
        revenus = simulation.calculate_add_divide('test_revenus', period.last_3_months)
        return revenus


@reference_formula
class test_revenus_3dm(SimpleFormulaColumn):
    column = FloatCol
    label = u"Revenus"
    entity_class = Individus

    def function(self, simulation, period):
        salaire = simulation.calculate('test_salaire', period.last_3_months)
        return  salaire


# Formules pour tester l'ajout des formules d'état

@reference_formula
class test_eligib_aide_Paris(SimpleFormulaColumn):
    column = BoolCol
    label = u"Eligibilite aide Paris"
    entity_class = Individus

    def function(self, simulation, period):
        resident_paris = simulation.calculate('test_resident_paris', period.this_year)
        return  resident_paris

