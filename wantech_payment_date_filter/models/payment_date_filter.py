from odoo import models, fields, api, _


class InvoiceFilter(models.Model):
    _inherit = 'account.invoice'

    payment_date = fields.Date(string="Paid Date", related='payment_ids.payment_date', store=True)