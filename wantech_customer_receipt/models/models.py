from odoo import models, fields


class Contacts(models.Model):
    _inherit = 'res.partner'

    print_receipt = fields.Boolean(string="Need Receipt")