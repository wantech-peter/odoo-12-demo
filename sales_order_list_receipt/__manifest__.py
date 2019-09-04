# -*- coding: utf-8 -*-
{
    'name': 'Sales Order List Receipt',
    'summary': "Provides the pdf report of invoice list.",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['base', 'sale', 'account'],
    'data': [
        'views/views.xml',
        'report/receipt_list_sales_order.xml',
        'report/receipt_list_account.xml',
        'report/receipt_list_account2.xml',
        'report/invoice_list_sales_order.xml',
        'report/reports.xml'
    ],
    'version': '1.0',
}
