# -*- coding: utf-8 -*-
{
    'name': 'WANTECH CONTACTS',
    'summary': "",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['contacts', 'account','sale'],
    'data': [
        'views/contact_updation.xml',
        'views/sale_carnum_view.xml',
        'views/account_carnum_view.xml',
        'views/inventory_cardetails_view.xml',

        'security/ir.model.access.csv',
    ],
    'license': 'AGPL-3',
    'version': '1.0',
    'installable': True,
}
