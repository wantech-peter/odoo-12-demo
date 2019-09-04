# -*- coding: utf-8 -*-
from odoo import models, api


class PickingListPDF(models.AbstractModel):
    _name = 'report.wantech_picking_category_report_order.favourite_pdf'

    def _get_report_values(self, docids, data=None):
        print(docids)
        return {
            'docids':data
        }

class ProductList(models.AbstractModel):
    _name = 'report.picking_list_report.report_list_product_category_car'
    _order = 'car_number asc, order asc'

    @api.model
    def _get_report_values(self, docids, data=None):

        query = """
            SELECT car_number,SUM(CAST(product_qty AS decimal)) as quantity,productname
            FROM report_test_stock_forecast_car
            WHERE id %s
            GROUP BY car_number,productname, report_test_stock_forecast_car.order
            ORDER BY car_number, report_test_stock_forecast_car.order
        """ % (str("in %s" % str(tuple(docids))) if len(docids) > 1 else (" = " + str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()

        products_grouped = {}
        car_numbers = []
        product_names = []
        for item in data:
            car_numbers.append(item["car_number"])
            product_names.append(item["productname"])
        car_numbers = list(set(car_numbers))
        car_numbers.sort()
        product_names = list(set(product_names))

        for product in data:
            products_grouped[(product['productname'], product['car_number'])] = {
                'productname': product['productname'],
                'car_num': product['car_number'],
                'quantity': product['quantity'],

            }
            asdasdas = products_grouped

        return {
            'doc_model': 'report.test.stock.forecast.car',
            'docs': data,
            'products_grouped': products_grouped,
            'car_numbers': car_numbers,
            'product_names': product_names,
        }
