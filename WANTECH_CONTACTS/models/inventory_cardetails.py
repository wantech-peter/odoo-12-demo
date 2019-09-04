from odoo import models, fields,api



class CarNumberinventory(models.Model):
    _inherit = "stock.picking"

    number_car = fields.Many2one(string="Car Number", related='partner_id.car_number', store=True, readonly=True)
    stop_number = fields.Integer(string="Stop Number", related="partner_id.customer_stopnum")