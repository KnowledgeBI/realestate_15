# -*- coding: utf-8 -*-
{
    'name': "Progress Bill",

    'summary': """Progress Bill""",

    'description': """
        Progress Bill
    """,

    'author': "Kareem & Mahmoud",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'uom',
        'sale',
        'sales_team',
        'sales_team_custom',
        'purchase',
        'analytic',
        'co_project',
        'co_customer_contract',
        'co_subcontractor_contract',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/invoice.xml',
        'views/bill.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/analytic.xml',
        'reports/progress_invoice_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
