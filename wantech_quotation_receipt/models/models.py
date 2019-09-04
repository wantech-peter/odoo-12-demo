from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    print_receipt = fields.Boolean(string="Need Receipt")
    sale_order = fields.Char(string="sale_order")