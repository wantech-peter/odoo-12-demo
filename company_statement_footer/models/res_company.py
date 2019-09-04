from odoo import api, fields, models, tools, _


class CompanyStatementFooter(models.Model):
    _inherit = 'res.company'

    statement_footer = fields.Text(string="Statement Footer")
