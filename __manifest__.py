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

        'wizard/make_report_parking_lot_views.xml',

        'report/parking_lot_reports.xml',
        'report/parking_lot_templates.xml',

        'views/parking_lot_views.xml',
        'views/parking_ticket_views.xml',
        'views/parking_vehicle_views.xml',
        'views/parking_lot_menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
