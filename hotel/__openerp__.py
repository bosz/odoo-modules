# -*- coding: utf-8 -*-
{
    'name': "Hotel",

    'summary': """
        Newest hotel module""",

    'description': """
        Long desc of new hotel module
    """,

    'author': "piarsolutions",
    'website': "http://www.piarsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hospitality',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'board'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/report.xml',
        'views/report_dashboard.xml',  
        'views/full_hotel_report.xml', 
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}