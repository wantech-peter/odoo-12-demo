# -*- coding: utf-8 -*-

from odoo import models, fields,api, _

class ContactUpdation(models.Model):
    _inherit = "res.partner"
    _order = "car_number,customer_stopnum,customer_stopnumber"

    customer_stopnum = fields.Integer(string="Stop Number", default=False, store=True)
    partner_number = fields.Char(string="Number")
    customer_stopnumber = fields.Integer(string="Stop Number", related="customer_stopnum")
    fax_number = fields.Char(string="Fax Number")
    car_number = fields.Many2one('car.number.option', string="Car number", store=True)
    customer_type = fields.Many2one('customer.type.option', string="Customer Type")



    @api.depends('supplier')
    @api.onchange('supplier')
    def _onchange_supplier(self):
        if self.supplier == True:
            self.customer = False


    @api.depends('customer')
    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer == True:
            self.supplier = False

class CarNumber(models.Model):
    _name = 'car.number.option'
    _rec_name = 'number'

    number = fields.Char(string="Number",required=True)

class CustomerType(models.Model):
    _name = 'customer.type.option'
    _rec_name = 'type'

    type = fields.Char(string="Type", required=True)







