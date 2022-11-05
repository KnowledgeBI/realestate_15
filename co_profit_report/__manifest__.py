# -*- coding: utf-8 -*-
{
    'name': 'Profit Report',
    'version': '15',
    'category': 'Account',
    'summary': '''
        Profit Report.
        ''',
    'author': 'Kareem Wazery',
    'license': "OPL-1",
    'depends': [
        'base',
        'account',
        'analytic',
        'co_project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/profit_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True
}
