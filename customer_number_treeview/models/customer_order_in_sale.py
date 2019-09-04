from odoo import models, api, fields, _


class OrderCustomerByParnerNum(models.Model):
    _inherit = 'res.partner'
    _order = 'partner_number'
