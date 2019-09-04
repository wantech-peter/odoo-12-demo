# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    payment_method_id = fields.Many2one('account.payment.method',
                                        string="Payment Method")
