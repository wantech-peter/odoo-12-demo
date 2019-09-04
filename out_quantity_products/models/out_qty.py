
from odoo import models, api, fields, _


class CustomerFields(models.AbstractModel):
    _inherit = "product.template"

    out_qty = fields.Float(string="Out quantity", compute="_get_out_quantity")

    @api.multi
    def _get_out_quantity(self):
        for rec in self:
            rec.out_qty = rec.qty_available - rec.virtual_available



