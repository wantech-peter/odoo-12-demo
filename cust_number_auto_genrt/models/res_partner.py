# -*- coding: utf-8 -*-
from odoo import models, fields,api, _


class AutoGenerateCustNumber(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        """Override 'create' function to auto generate the customer number for customers only."""
        for vals in vals_list:
            if vals.get('customer'):
                seqs = self.env['ir.sequence'].search(
                    [('code', '=', 'CUSTOMER_NUMBER')])  # Find out the sequence defined for Customer Number
                if seqs:
                    seq_number = self.env['ir.sequence'].next_by_code('CUSTOMER_NUMBER')
                    vals.update({
                        'partner_number': seq_number if seq_number else 0,
                    })
        return super(AutoGenerateCustNumber, self).create(vals_list)

    @api.depends('is_company', 'name', 'partner_number', 'parent_id.name', 'type', 'company_name')
    def _compute_display_name(self):
        """Rewrite the compute function to change the display name when 'partner_number' field change"""
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)
