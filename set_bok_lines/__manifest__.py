# -*- coding: utf-8 -*-
{
    'name': "set_bok_lines",

    'summary': """
        set_bok_lines
        """,

    'description': """
        set_bok_lines
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'purchase',
        # 'adding_analytic_account',
        'sale',
        'stock',
        'stock_analytic',
        'co_project',
        'account',
        # 'progress_invoice',
        # 'subcontract',
        'co_customer_contract',
        # 'subcontract_requisition',
        # 'custom_purchase_alshams',
        'purchase_agreement_custom',
        'purchase_requisition',
        'analytic',

    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'views/views.xml',
        'views/wizard.xml',
        'views/boq_line.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
