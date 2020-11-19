# -*- coding: utf-8 -*-
{
    'name': "Parking Lot",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/report_paperformat.xml',
        'data/parkingtickets_data.xml',
        'data/ir_cron_parkinglot.xml',

        'views/templates.xml',
        'views/parkinglot.xml',

        'wizard/report_wizard_parkinglot_view.xml',

        'report/report_parkinglot.xml',
        'report/report_parkinglot_templates.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
