# -*- coding: utf-8 -*-
{
    'name': 'Picking List Report',
    'summary': "Provides the pdf report of Picking list.",
    'author': 'WANTECH Innovation Technology Ltd',
    'website': "http://www.wantech.com.hk",
    'depends': ['base', "product", 'account'],
    'data': [
        'views/views.xml',
        'report/picking_report_template.xml',
        'report/picking_report_template3.xml',
        'report/picking_report_template_kb.xml',
        'report/picking_report_template_pk.xml',
        'report/picking_car_number_report_template.xml',
        'report/picking_report_template_by_page.xml',
        'report/product_list.xml',
        'report/reports.xml'
    ],
    'license': 'AGPL-3',
    'version': '1.1',
    'installable': True
}


