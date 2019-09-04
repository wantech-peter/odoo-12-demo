
# -*- coding: utf-8 -*-
{
    'name': 'Need receipt in SO',
    'summary': "",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['sale', 'wantech_customer_receipt', 'wantech_quotation_receipt'],
    'data': [
        'views/sign_back_field.xml',
        'security/ir.model.access.csv'
    ],
    'license': 'AGPL-3',
    'version': '1.0',
    'installable': True,
}
