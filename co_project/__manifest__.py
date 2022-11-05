# -*- coding: utf-8 -*-
{
    'name': "Contracting Project",

    'summary': """Contracting Project""",

    'description': """
        Contracting Project
    """,

    'author': "Kareem Wazery",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '15',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'analytic',
        'stock',
    ],

    # always loaded
    'data': [
        'views/analytic_account.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
