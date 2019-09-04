from odoo import models, fields





class salecarnum(models.Model):
    _inherit = "sale.order"

    car_number = fields.Many2one(string="Car Number", related='partner_id.car_number', store=True, readonly=True)

