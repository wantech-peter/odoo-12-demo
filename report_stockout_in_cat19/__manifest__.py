# -*- coding: utf-8 -*-
{
    'name': "report.stockout.in.cat19",

    'summary': """
        """,

    'description': """
    """,

    'author': "wantech",
    'website': "http://www.wantech.com.hk",
    'category': 'reporting',
    'version': '12.0.1.0.0',
    'depends': ['base',"sale_management"],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
}