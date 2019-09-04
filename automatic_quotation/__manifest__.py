# -*- coding: utf-8 -*-
{
    'name': 'Automatic Quotation Generation',
    'summary': "",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['contacts', 'sale_management', 'website_sale'],
    'data': [
        'views/generate_view.xml',
        'data/cron.xml'
    ],
    'license': 'AGPL-3',
    'version': '1.0',
    'installable': True,
    'application': True,
    'auto_install': False,
}
