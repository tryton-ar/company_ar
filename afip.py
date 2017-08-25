# -*- coding: utf-8 -*-
# This file is part of the party_ar module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

#Update afip tables from afip.
#http://www.sistemasagiles.com.ar/trac/wiki/FacturaElectronicaExportacion#TablasdePar%C3%A1metros

from pyafipws.wsfev1 import WSFEv1
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
import logging
logger = logging.getLogger(__name__)

__all__ = ['AFIPTables', 'AFIPCountry']


class AFIPTables(ModelView):
    'AFIP Tables'
    __name__ = 'afip.tables'

    @classmethod
    def __setup__(cls):
        super(AFIPTables, cls).__setup__()
        cls._buttons.update({
            'import_afip_countrys': {},
        })

    @classmethod
    @ModelView.button
    def import_afip_countrys(cls, configs):
        '''
        Import AFIP countrys.
        '''
        pool = Pool()
        Company = pool.get('company.company')
        AFIPCountry = pool.get('afip.country')
        company = Company(Transaction().context.get('company'))
        service = 'wsfe'
        auth_data = company.pyafipws_authenticate(service=service)
        ws = WSFEv1()
        if company.pyafipws_mode_cert == 'homologacion':
            WSDL = 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL'
        elif company.pyafipws_mode_cert == 'produccion':
            WSDL = (
                'https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL')
        else:
            logger.error('Webservice not configured!')
            return
        cache_dir = company.get_cache_dir()
        ws.Conectar(wsdl=WSDL, cache=cache_dir)
        ws.Cuit = company.party.vat_number
        ws.Token = auth_data['token']
        ws.Sign = auth_data['sign']
        countrys = ws.ParamGetTiposPaises(sep=';')
        for country in countrys:
            afip_country = AFIPCountry()
            (code, name) = country.split(';')
            try:
                country_tmp, = AFIPCountry.search([('code', '=', code)])
            except ValueError:
                afip_country.code = code
                afip_country.name = name
                afip_country.save()
                Transaction().cursor.commit()
            logger.info('code: %s; dst: %s' % (code, name))

    @classmethod
    def cron_afip_tables(cls, args=None):
        '''
        Cron import country_dst.
        '''
        logger.info('Start Scheduler cron afip table.')
        cls.import_afip_countrys(args)
        logger.info('End Scheduler cron afip table.')


class AFIPCountry(ModelSQL, ModelView):
    'AFIP Country'
    __name__ = 'afip.country'

    code = fields.Char('Code')
    name = fields.Char('Name')
