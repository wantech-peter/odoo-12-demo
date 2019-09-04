# from odoo import models,fields
#
#
# class ConfirmPayment(models.TransientModel):
#     _name = 'confirm.payment'
#
#     account_debit = fields.Many2one('account.account',string='Debit Account')
#     currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
#     payment_amount = fields.Monetary(string='Payment Amount', required=True)
#     payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
#     payment_memo = fields.Char(string='Memo')
#     payment_journal = fields.Many2one('account.journal', string='Payment Journal', required=True,
#                                  domain=[('type', 'in', ('bank', 'cash'))])
#     payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)
#     reconcile_difference_handling = fields.Selection([('reconcile', 'Mark invoice as fully paid')], string="Payment Difference Handling", copy=False)
#     writeoff_account = fields.Many2one('account.account', string="Difference Account",
#                                           domain=[('deprecated', '=', False)], copy=False)
#     label_writeoff = fields.Char(
#         string='Journal Item Label',
#         help='Change label of the counterpart that will hold the payment difference',
#         default='Write-Off')
#
#     def validate_payment(self):
#         print("jjjjjjjjjjj")
#         invoice_ids = self._context.get('active_ids')
#         payment_ids = self.env['account.invoice'].browse(invoice_ids).\
#             filtered(lambda x: x.state == 'paid')
#         print("ffff",payment_ids)
#         # for rec in payment_ids:
#         #     print("ggggg")
#         #     line_obj = self.env['stock.move'].search([('picking_id', '=', rec.id)])
#         #     for val in line_obj:
#         #         val.quantity_done = val.product_uom_qty
#         #         rec.button_validate()
#
