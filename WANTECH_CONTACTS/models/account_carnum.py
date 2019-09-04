from odoo import models, fields,api, _




class CarNumberaccount(models.Model):
    _inherit = "account.invoice"

    number_car = fields.Many2one(string="Car Number", related='partner_id.car_number', store=True, readonly=True)

