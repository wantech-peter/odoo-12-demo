# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def action_move_create(self):
        for inv in self:
            if not inv.date_invoice:
                inv.write({'date_invoice': inv.sale_order.quotation_date})
        return super(AccountInvoice, self).action_move_create()
