# -*- coding: utf-8 -*-
{
    'name': 'Followup Report Statement',
    'summary': "Followup Report Statement",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['account','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'security/statement_report.xml',
        'views/views.xml',
    ],
    'license': 'AGPL-3',
    'version': '1.0',
    'installable': True,
    'application': True,
    'auto_install': False,
}


