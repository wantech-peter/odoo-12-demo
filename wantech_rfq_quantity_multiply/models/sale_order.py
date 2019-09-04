# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = 'purchase.order'

    select_multiply = fields.Selection([(2, '2'), (3, '3'), (4, '4'), (5, '5')])

    def multiply_quantity(self):
        for line in self.order_line:
            if line:
                if self.select_multiply:
                   print(type(self.select_multiply))
                   line.update({
                       'product_qty': line.product_qty * int(self.select_multiply)
                   })


