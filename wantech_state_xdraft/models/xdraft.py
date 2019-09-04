from odoo import models, fields, api, _


class InvoiceStateXdraft(models.Model):
    _inherit = 'account.invoice'

    state = fields.Selection(selection_add=[('xdraft', 'Xdraft')])