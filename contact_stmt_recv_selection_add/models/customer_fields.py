# -*- coding: utf-8 -*-

from odoo import models, fields


class CustomerFieldsExtend(models.AbstractModel):
    _inherit = "res.partner"

    statement_type = fields.Selection(selection_add=[
            ('urgent_fax', 'Urgent Fax'),
            ('urgent_whatsapp', 'Urgent Whatsapp'),
            ('urgent_email', 'Urgent Email'),
        ], string='Statement Type')
