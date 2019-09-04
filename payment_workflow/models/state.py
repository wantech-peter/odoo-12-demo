from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare
from itertools import groupby


class InvoiceState(models.Model):
    _inherit = 'account.invoice'

    state = fields.Selection(selection_add=[('bank_verified', 'Bank Verified')])