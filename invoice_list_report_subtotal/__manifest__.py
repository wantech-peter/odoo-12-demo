# -*- coding: utf-8 -*-
{
    'name': 'Invoice List Report with Customer Subtotal',
    'summary': "Provides the pdf report of invoice list with Customer Subtotal.",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['base', 'account'],
    'data': [
        'report/invoice_report_template.xml',
        'report/invoice_report_template2.xml',
        'report/reports.xml'
    ],
    'license': 'AGPL-3',
    'version': '1.0',
    'installable': True,
    'application': True,
    'auto_install': False,
}


