# -*- coding: utf-8 -*-

{
    'name': "Real Estate - Maintenance",
    'version': "14.0.1.1",
    'author': "IDT",
    'category': "Real Estate",
    'summary': '',
    'description': '''
        ''',
    'depends': ['base_setup',
                'itsys_real_estate',
                'repair',
                'website'],
    'data': [
        'views/repair_order_view.xml',
        'views/maintenance_portal_templates.xml',
        'views/repair_portal_form.xml',
        'views/properties_view.xml',
    ],
    'demo': [],
    "website" : "https://www.i-datatech.com",
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
