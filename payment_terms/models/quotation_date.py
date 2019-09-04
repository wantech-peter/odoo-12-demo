from odoo import models, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta


class QuotationDate(models.Model):
    _inherit = "sale.order"

    quotation_date = fields.Date(string='Quotation Date', default=fields.Date.to_string((datetime.now() + relativedelta(days=+1)).date()))


