
from odoo import models, api, fields, _


class CancelDeleteInvoice(models.Model):
    _inherit = "sale.order"

    @api.multi
    def cancel_so(self):
        return self.write({'state': 'cancel'})