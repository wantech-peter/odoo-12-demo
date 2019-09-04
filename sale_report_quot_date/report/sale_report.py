# -*- coding: utf-8 -*-


from odoo import models, fields


class SaleReportInherit(models.Model):
    """ Inherit sale report to add a customized field 'quotation date' to the 'add custom filter'
       option in pivot report """
    _inherit = 'sale.report'

    quotation_date = fields.Date('Quotation Date', readonly=True)  # adding the field to the report.

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['quotation_date'] = ', s.quotation_date as quotation_date'  # get the quotation date

        return super(SaleReportInherit, self)._query(with_clause, fields, groupby, from_clause)
