# -*- coding: utf-8 -*-

from odoo import models,api,fields


class NeedReceiptSale(models.Model):
    _inherit = "sale.order"
    sign_back = fields.Boolean(string="Sign Back", readonly=True)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(NeedReceiptSale, self).onchange_partner_id()
        if self.partner_id.print_receipt == True:
            self.update({

                'print_receipt': True,
            })
        else:
            self.update({

                'print_receipt': False,
            })
        return res


class SignBackUpdatePrice(models.Model):
    _name = 'sign.back.update.wizard'


    @api.multi
    def sign_back_update(self):
        active_ids = self._context.get('active_ids')
        order_ids = self.env['sale.order'].browse(active_ids)
        for line in order_ids:
            line.sign_back = True

