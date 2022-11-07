# -*- coding: utf-8 -*-
{
    'name': "Purchase Agreement",
    'description': """
        Add ability to create Purchase Agreement
    """,
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase_requisition'],

    # always loaded
    'data': [
        'views/views.xml',
        'reports/format.xml',
        'reports/layout.xml',
        'reports/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}