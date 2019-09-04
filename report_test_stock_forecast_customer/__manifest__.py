# -*- coding: utf-8 -*-
{
    'name': "report_test_stock_forecast_customer",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "wantech",
    'website': "http://www.wantech.com.hk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'peter',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base',"stock","product"],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',
        'views/views.xml',
        'report/product_list.xml',
        'report/reports.xml'
    ],
    'installable': True,
    # only loaded in demonstration mode
}