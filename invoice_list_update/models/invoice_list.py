from odoo import models, fields,api


class InvoiceListView(models.Model):
    _inherit = 'account.invoice'
    invoice_partner = fields.Char(string='Customer Number', related='partner_id.partner_number',store=True)





