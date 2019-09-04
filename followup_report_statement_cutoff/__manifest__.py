# -*- coding: utf-8 -*-
{
    'name': 'Report Statement Cutoff',
    'summary': "Report Statement Cutoff",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['account','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'security/statement_report_cutoff.xml',
        'views/views.xml',
    ],
    'license': 'AGPL-3',
    'version': '1.0',
    'installable': True,
    'application': True,
    'auto_install': False,
}


