# -*- coding: utf-8 -*-
{
    'name': 'Sales Team Custom',
    'summary': 'Sales Team Custom',
    'version': '13.0.0',
    'category': 'sale',
    'author': '',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        'sale_stock',
        'sales_team',
        'purchase',
        'account',
    ],
    'data': [
        'views/purchase.xml',
        'views/picking.xml',
        'views/valuation_layer.xml',
        'views/account_move.xml',
    ],
    'application': True,
}
