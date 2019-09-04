from itertools import groupby
from odoo import models, api


class ProductList(models.AbstractModel):
    _name = 'report.picking_list_report.report_list_picking_by_page'

    @api.model
    def _get_report_values(self, docids, data=None):

        stock = self.env['report.test.stock.forecast']
        result_vals = []
        values = stock.browse(docids)
        for key, item in groupby(values, lambda k: k.car_number):
            result_vals.append(dict(name=key, data=[
                {
                    'custno': d.custno,
                    'custname': d.custname,
                    'unit': d.unit,
                    'product_qty': d.product_qty,
                    'productname': d.productname,
                    'sono': d.sono
                } for d in item]))

        return {
            'docs': result_vals,
        }