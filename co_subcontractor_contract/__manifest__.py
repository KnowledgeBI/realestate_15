# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Subcontractor Contract",
    'version': "15",
    'category': "Purchases",
    'description': """
     Subcontractor Contract
     """,
    'author': "Kareem Wazery",
    'website': "",
    'depends': [
        'base',
        'sale_management',
        'purchase',
        'co_project',
        'co_customer_contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/res_partner.xml',
        'views/contract.xml',
        'views/category_order.xml',
    ],
    'installable': True,
    'application': False,
    # 'live_test_url': 'https://youtu.be/wS4f9hEABxY',
}
