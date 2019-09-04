from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"


class InvoiceState(models.Model):
    _inherit = 'account.invoice'

    sale_order = fields.Many2one('sale.order', string='sale order')
    quot_date = fields.Date(string="Quotation Date", related='sale_order.quotation_date', store=True)
