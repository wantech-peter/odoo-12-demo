# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplateInherit(models.Model):
    """ Inherit product.template model to add the field commission percentage """
    _inherit = 'product.template'

    commission_percent = fields.Char(string='Commission %')  # adding the field to the model.
