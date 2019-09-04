from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.account.models.account_payment import account_abstract_payment
from odoo.tools import float_compare
from itertools import groupby


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': -1,
    'out_refund': 1,
}


class account_abstract_payment_inherit(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    @api.model
    def default_get(self, fields):
        print("ente firsttttttt")
        rec = super(account_abstract_payment , self).default_get(fields)
        print("enet secondddddddddddd")
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.invoice':
            return rec

        invoices = self.env['account.invoice'].browse(active_ids)

        # Check all invoices are open
        if any(invoice.state not in ['open', 'confirmed_paid'] for invoice in invoices):
            raise UserError(_("You can only register payments for open or paid confirmed invoices"))

        # Check all invoices have the same currency
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

        # Look if we are mixin multiple commercial_partner or customer invoices with vendor bills
        multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
                    or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
                    or inv.account_id != invoices[0].account_id
                    or inv.partner_bank_id != invoices[0].partner_bank_id
                    for inv in invoices)

        currency = invoices[0].currency_id

        total_amount = self._compute_payment_amount(invoices=invoices, currency=currency)

        rec.update({
            'amount': abs(total_amount),
            'currency_id': currency.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': False if multi else invoices[0].commercial_partner_id.id,
            'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'communication': ' '.join([ref for ref in invoices.mapped('reference') if ref]),
            'invoice_ids': [(6, 0, invoices.ids)],
            'multi': multi,
        })
        return rec

    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        print("selff1111",self)

        '''Compute the total amount for the payment wizard.

        :param invoices: If not specified, pick all the invoices.
        :param currency: If not specified, search a default currency on wizard/journal.
        :return: The total amount to pay the invoices.
        '''

        # Get the payment invoices
        if not invoices:
            invoices = self.invoice_ids

        # Get the payment currency
        if not currency:
            currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or invoices and invoices[0].currency_id

        # Avoid currency rounding issues by summing the amounts according to the company_currency_id before
        total = 0.0
        groups = groupby(invoices, lambda i: i.currency_id)
        state_paid = False
        for i in invoices:
            state_paid = False
            if i.state == 'confirmed_paid':
                state_paid = True

        for payment_currency, payment_invoices in groups:

            if not state_paid:
                amount_total = sum([MAP_INVOICE_TYPE_PAYMENT_SIGN[i.type] * i.residual_signed for i in payment_invoices])

            if state_paid:
                amount_total = sum([MAP_INVOICE_TYPE_PAYMENT_SIGN[i.type] * i.amount_total_signed for i in payment_invoices])

            if payment_currency == currency:
                total += amount_total
            else:
                total += payment_currency._convert(amount_total, currency, self.env.user.company_id, self.payment_date or fields.Date.today())
        return total

    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.invoice'].browse(active_ids)

        # Check all invoices are open
        print("self.is_bank_verifynnananaanna",self.is_bank_verify)
        if any(invoice.state != 'confirmed_paid' for invoice in invoices):
            self.is_bank_verify = True
        print("is_bank_verifyis_bank_verify")
        jrnl_filters = self._compute_journal_domain_and_types()
        journal_types = jrnl_filters['journal_types']
        domain_on_types = [('type', 'in', list(journal_types))]
        if self.journal_id.type not in journal_types:
            self.journal_id = self.env['account.journal'].search(domain_on_types, limit=1)
        return {'domain': {'journal_id': jrnl_filters['domain'] + domain_on_types}}




class account_payment_inherit(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        print("selff222222", self)

        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:


            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state not in ['open','confirmed_paid'] for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open or paid confirmed!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                    sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(
                    lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})
        return True
        
    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
            if self.my_debit_account_id:
                self.destination_account_id = self.journal_id.default_credit_account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            print("self.partner_idself.partner_id")
            if self.partner_type == 'customer':
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
                if self.my_debit_account_id:
                    self.destination_account_id = self.journal_id.default_credit_account_id.id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id.id
                if self.my_debit_account_id:
                    self.destination_account_id = self.journal_id.default_credit_account_id.id
        elif self.partner_type == 'customer':
    
            default_account = self.env['ir.property'].get('property_account_receivable_id', 'res.partner')
            self.destination_account_id = default_account.id
            if self.my_debit_account_id:
                self.destination_account_id = self.journal_id.default_credit_account_id.id
        elif self.partner_type == 'supplier':
            default_account = self.env['ir.property'].get('property_account_payable_id', 'res.partner')
            self.destination_account_id = default_account.id    

    def _get_liquidity_move_line_vals(self, amount):
        
        name = self.name

        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound','transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }
        if self.my_debit_account_id:
            vals.update({
                'account_id': self.my_debit_account_id.id
            })
        print(vals)

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id._convert(amount, self.journal_id.currency_id, self.company_id, self.payment_date or fields.Date.today())
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date)._compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

class AccountAbstractPaymnet(models.AbstractModel):

    _inherit = "account.abstract.payment"

    my_debit_account_id = fields.Many2one('account.account',string="Debit Account",domain=[('deprecated', '=', False)])
    is_bank_verify = fields.Boolean(string="Is Bank Verified", default=False)

class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    my_debit_account_id  = fields.Many2one('account.account',string="Debit Account",domain=[('deprecated', '=', False)])

    @api.model
    def default_get(self, fields):
        print("avarude level2")
        rec = super(account_register_payments, self).default_get(fields)
        print("avarude level2 nextt")
        active_ids = self._context.get('active_ids')

        if not active_ids:
            raise UserError(_("Programming error: wizard action executed without active_ids in context."))

        return rec

    @api.multi
    def create_payments(self):

        '''Create payments according to the invoices.
        Having invoices with different commercial_partner_id or different type (Vendor bills with customer invoices)
        leads to multiple payments.
        In case of all the invoices are related to the same commercial_partner_id and have the same type,
        only one payment will be created.

        :return: The ir.actions.act_window to show created payments.
        '''
        Payment = self.env['account.payment']
        payments = Payment
        for payment_vals in self.get_payments_vals():
            print("payment_valssssssssssssss", payment_vals)
            payments += Payment.create(payment_vals)
        payments.post()

        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        for rec in self.invoice_ids:
            if rec.state == 'confirmed_paid':
                rec.update({
                    'state': 'bank_verified'
                })
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals

    @api.multi
    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.

        :param invoices: The invoices that should have the same commercial partner and the same type.
        :return: The payment values as a dictionary.
        '''
        amount = self._compute_payment_amount(invoices=invoices) if self.multi else self.amount
        payment_type = ('inbound' if amount > 0 else 'outbound') if self.multi else self.payment_type
        bank_account = self.multi and invoices[0].partner_bank_id or self.partner_bank_account_id
        pmt_communication = self.show_communication_field and self.communication \
                            or self.group_invoices and ' '.join([inv.reference or inv.number for inv in invoices]) \
                            or invoices[
                                0].reference  # in this case, invoices contains only one element, since group_invoices is False

        print("yureeekkkkaaaaaaaaaaaaaa", self.journal_id.id, self.my_debit_account_id.id,
              self.my_debit_account_id.id, )
        values = {
            'journal_id': self.journal_id.id,
            'my_debit_account_id': self.my_debit_account_id.id or '',
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': pmt_communication,
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': payment_type,
            'amount': abs(amount),
            'currency_id': self.currency_id.id,
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'partner_bank_account_id': bank_account.id,
            'multi': False,
            'payment_difference_handling': self.payment_difference_handling,
            'writeoff_account_id': self.writeoff_account_id.id,
            'writeoff_label': self.writeoff_label,
        }

        return values
