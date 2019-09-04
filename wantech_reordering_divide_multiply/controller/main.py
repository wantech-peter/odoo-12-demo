""" Creating an http root to accept and process request from JavaSCript."""
from odoo import models, api


class UpdateReorderingQuantModel(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.model
    def quantity_update(self, kwargs):
        query = """UPDATE stock_warehouse_orderpoint SET product_min_qty = product_min_qty """ + """%s %s""" % (
            kwargs['operator'], kwargs[
                'value']) + """, product_max_qty = product_max_qty """ + """%s %s""" % (
                    kwargs['operator'], kwargs['value'])
        cr = self._cr
        try:
            cr.execute(query)
            return True
        except Exception as e:
            return False

