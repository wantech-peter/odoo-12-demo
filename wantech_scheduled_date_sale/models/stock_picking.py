from odoo import models, fields,api, _


class AccountAbstractPaymentInherit(models.AbstractModel):
    """Rewriting the compute function of scheduled date to set as quotation date of
       curresponding sale order"""
    _inherit = "stock.picking"

    @api.one
    @api.depends('move_lines.date_expected')
    def _compute_scheduled_date(self):

        if self.move_type == 'direct':
            self.scheduled_date = min(self.move_lines.mapped('date_expected') or [fields.Datetime.now()])
        else:
            self.scheduled_date = max(self.move_lines.mapped('date_expected') or [fields.Datetime.now()])

        if self.sale_id and self.sale_id.quotation_date:
            self.scheduled_date = str(self.sale_id.quotation_date)

