# -*- coding: utf-8 -*-
{
    'name': "Customer Contract",

    'summary': """Customer Contract""",

    'description': """
        Customer Contract
    """,

    'author': "Kareem Wazery",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '15',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'uom',
        'sale',
        'analytic',
        'sale_margin',
        'co_project',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/menu.xml',
        'views/boq_line.xml',
        'views/contract.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
