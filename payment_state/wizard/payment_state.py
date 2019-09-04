from odoo import models, fields, _
from odoo.exceptions import UserError


class ConfirmPayment(models.TransientModel):
    _name = 'confirm.payment'

    def confirm_paid(self):
        active_invoices = self._context.get('active_ids')
        my_invoices = self.env['account.invoice'].browse(active_invoices)
        if any(invoice.state not in ['paid'] for invoice in my_invoices):
            raise UserError(_("You can only Confirm paid for paid invoices"))
        active_invoices = self.env['account.invoice'].browse(active_invoices).\
            filtered(lambda x: x.state == 'paid')
        for rec in active_invoices:
            rec.state = 'confirmed_paid'


class InvoiceState(models.Model):
    _inherit = 'account.invoice'

    state = fields.Selection(selection_add=[('confirmed_paid', 'Paid Confirmed')])
