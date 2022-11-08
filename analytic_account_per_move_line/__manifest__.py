
{
    'name': 'Analytic Account Per Move Line',
    'summary': 'Analytic Account Per Move Line',
    'author': "Mahmoud Elfeky",
    'version': '15.0.0.1.0',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'account',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'report/',
        # 'wizard/',
        'views/account_move.xml',
        # 'data/',
    ],
    'demo': [
        # 'demo/',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

