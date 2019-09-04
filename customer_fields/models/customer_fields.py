
from odoo import models, api, fields, _
from odoo.tools.misc import formatLang, format_date


class CustomerFields(models.AbstractModel):
    _inherit = "res.partner"

    statement_letter = fields.Boolean(string='Statement Letter')
    statement_type = fields.Selection([
            ('normal', 'Normal'),
            ('whats_app', 'Whatsapp'),
            ('email', 'Email'),
            ('no_need', 'No Need'),
            ('fax', 'Fax'),
            ('whats_app_email', 'Whatsapp & Email'),
        ], string='Statement Type')
    statement_receive = fields.Selection([
            ('AMY', 'AMY'),
            ('運輸', '運輸'),
            ('寄封', '寄封'),
            ('收票', '收票'),
            ('入數', '入數'),
            ('寄', '寄'),
        ], string='Statement Receive')
    whats_app_num = fields.Char(string="Whatsapp No")