from odoo import models, fields


class ContactPerson(models.Model):
    _inherit = "sale.order"

    contact_number = fields.Char(string="Phone", related='partner_id.phone')
    contact_person = fields.Char(string="Contact Person", related='partner_id.my_contact_person')