from odoo import models, fields,api, _




class ContactPerson(models.Model):
    _inherit = "res.partner"

    my_contact_person = fields.Char(string="Contact Person")
#
