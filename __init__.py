# This file is part of the company_ar module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from . import company
from . import afip


def register():
    Pool.register(
        company.Company,
        afip.AFIPTables,
        afip.AFIPCountry,
        module='company_ar', type_='model')
