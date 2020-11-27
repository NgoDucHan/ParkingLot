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
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/ir_cron_parking_lot.xml',
        'data/parking_ticket_data.xml',
        'data/report_paperformat.xml',

        'wizard/report_wizard_parking_lot_view.xml',

        'report/report_parking_lot.xml',
        'report/report_parking_lot_templates.xml',

        'views/parking_lot.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
