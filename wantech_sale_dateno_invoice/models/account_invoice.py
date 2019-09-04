# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AcoountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order = fields.Many2one('sale.order', string="Sale Order")

    def action_invoice_open(self):
        res = super(AcoountInvoice, self).action_invoice_open()
        for invoice in self:
            if invoice.sale_order.id:
                invoice.number = invoice.sale_order.name
                invoice.reference = invoice.sale_order.name
                invoice.date_invoice = invoice.sale_order.quotation_date
        return res
