""" Inheriting Sale  Order to add Car Number Integer Field"""
from odoo import models, fields


class SaleOrder(models.Model):
    """ Inheriting Sale  Order to add Car Number Integer Field"""
    _inherit = 'sale.order'

    car_number_int = fields.Integer(string="車號")
