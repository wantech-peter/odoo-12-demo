# -*- coding: utf-8 -*-
{
    'name': 'Invoice List Report With Group Total',
    'summary': "Provides the pdf report of invoice list. With Group Total.",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['base', 'account'],
    'data': [
        'report/invoice_report_template.xml',
        'report/reports.xml'
    ],
    'license': 'AGPL-3',
    'version': '1.0',
    'installable': True,
    'application': True,
    'auto_install': False,
}


