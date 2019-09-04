import base64
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

class CompanySignature(models.Model):
    _inherit = 'res.company'

    signature_pic = fields.Binary(string="Signature Picture", readonly=False)
