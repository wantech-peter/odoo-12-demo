from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_validate_invoice_payment(self):
        for payment in self:
            for invoice in payment.invoice_ids:
                invoice.payment_method_id = payment.payment_method_id.id
        return super(AccountPayment, self).action_validate_invoice_payment()