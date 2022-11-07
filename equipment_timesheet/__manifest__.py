# -*- coding: utf-8 -*-
{
    'name': 'equipment_timesheet',
    'summary': 'equipment_timesheet',
    'description': '''equipment_timesheet
	''',
    'website': '',
    'category': 'general',
    'version': '15',
    'depends': [
        'base',
        'sale',
        'analytic',
        'co_customer_contract',
        'co_subcontractor_contract',
        'account'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/equipment_timesheet.xml',
        'views/labr_timesheet.xml',
    ],

    'installable': True,
    'application': True,

}
