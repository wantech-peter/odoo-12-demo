# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)

        self.amount_total = int(self.amount_untaxed + self.amount_tax) if self.payment_term_id.id not in [3,12] else (self.amount_untaxed + self.amount_tax)

        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id,
                                                               self.company_id,
                                                               self.date_invoice or fields.Date.today())
            amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id,
                                                         self.company_id, self.date_invoice or fields.Date.today())
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):

        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id == self.account_id:
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = line.currency_id or line.company_id.currency_id
                    residual += from_currency._convert(line.amount_residual, self.currency_id, line.company_id,
                                                       line.date or fields.Date.today())

        self.residual_company_signed = int(abs(residual_company_signed) * sign) if self.payment_term_id.id not in [3,12] else abs(residual_company_signed) * sign
        self.residual_signed = int(abs(residual) * sign) if self.payment_term_id.id not in [3,12] else abs(residual) * sign
        self.residual = int(abs(residual)) if self.payment_term_id.id not in [3,12] else abs(residual)

        if self.payment_term_id.id not in [3,12]:
            if float(self.residual) >=1 and float(self.residual) <3:
                self.residual = 0.0
                self.residual_signed = 0.0
                self.residual_company_signed = 0.0

        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue

            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    # if self.payment_term_id.id not in [3, 12]: # Extra added code, to resolve the round off issue.
                    #     print("ddddddd",t[1])
                    #     t_total = int(t[1])
                    #     total = int(total)

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:

                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)
            line = inv.finalize_invoice_move_lines(line)

            if inv.payment_term_id:   # Extra added code, to resolve the round off issue.
                if self.payment_term_id.id not in [3, 12]:
                    for check_line in line:
                        if check_line[2]:
                            if check_line[2]['debit']:
                                check_line[2]['debit'] = int(check_line[2]['debit'])

                            if check_line[2]['credit']:
                                check_line[2]['credit'] = int(check_line[2]['credit'])


            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            move = account_move.create(move_vals)
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post(invoice = inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    roundof_discount = fields.Monetary(string="Discount", compute="_amount_all",store=True)

    @api.depends('order_line.price_total')
    def _amount_all(self):

        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'roundof_discount': (amount_untaxed + amount_tax) - int(amount_untaxed + amount_tax) if order.payment_term_id.id not in [3,12] else 0,

                'amount_total': int(amount_untaxed + amount_tax) if order.payment_term_id.id not in [3,12] else (amount_untaxed + amount_tax),

            })

    @api.model
    def create(self, values):
        res = super(SaleOrderInherit, self).create(values)

        if res.state != 'sale':
            for line in res.order_line:
                if line.product_uom_qty == 0:
                    line.unlink()

        for line in res.order_line:
            for templ_line in res.sale_order_template_id.sale_order_template_line_ids:
                if line.product_id.id == templ_line.product_id.id:
                    line.update({
                        'price_unit': templ_line.price_unit,
                    })

        for line in res.sale_order_option_ids:
            for option_line in res.sale_order_template_id.sale_order_template_line_ids:
                if line.product_id.id == option_line.product_id.id:
                    line.update({
                        'price_unit': option_line.price_unit,
                    })

        if res.amount_total < 150:
            print("res.amount_total", res.amount_total)
            if self.env.user.has_group('sales_team.group_sale_manager') is False:
                raise UserError("Amount should be greater than 150")
        return res

    @api.multi
    def action_confirm(self):
        if self.amount_total < 150:
            if self.env.user.has_group('sales_team.group_sale_manager') is False:
                raise UserError("Amount should be greater than 150")
        res = super(SaleOrderInherit, self).action_confirm()
        return res

    @api.multi
    def write(self, values):
        res = super(SaleOrderInherit, self).write(values)
        if self.state != 'sale':
            if not self.is_quot_reload:
                for line in self.order_line:
                    if line.product_uom_qty == 0:
                        line.unlink()

        for line in self.order_line:
            for templ_line in self.sale_order_template_id.sale_order_template_line_ids:
                if line.product_id.id == templ_line.product_id.id:
                    line.update({
                        'price_unit': templ_line.price_unit,
                    })

        for line in self.sale_order_option_ids:
            for option_line in self.sale_order_template_id.sale_order_template_line_ids:
                if line.product_id.id == option_line.product_id.id:
                    line.update({
                        'price_unit': option_line.price_unit,
                    })

        if self.amount_total < 150:
            if self.env.user.has_group('sales_team.group_sale_manager') is False:
                raise UserError("Amount should be greater than 150")
        return res

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        if not self.sale_order_template_id:
            self.require_signature = self._get_default_require_signature()
            self.require_payment = self._get_default_require_payment()
            return
        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)

        order_lines = [(5, 0, 0)]
        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_template_change(line)

            if line.product_id:
                discount = 0
                if self.pricelist_id:
                    if not self.sale_order_template_id:
                        price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(
                            line.product_id, 1, False)
                        if self.pricelist_id.discount_policy == 'without_discount' and line.price_unit:
                            discount = (line.price_unit - price) / line.price_unit * 100
                            price = line.price_unit
                    if self.sale_order_template_id:
                        price = line.price_unit
                else:
                    price = line.price_unit

                data.update({
                    'price_unit': price,
                    'discount': 100 - ((100 - discount) * (100 - line.discount) / 100),
                    'product_uom_qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'customer_lead': self._get_customer_lead(line.product_id.product_tmpl_id),
                })
                if self.pricelist_id:
                    if not self.sale_order_template_id:
                        data.update(self.env['sale.order.line']._get_purchase_price(self.pricelist_id, line.product_id,
                                                                                    line.product_uom_id,
                                                                                    fields.Date.context_today(self)))
            order_lines.append((0, 0, data))

        self.order_line = order_lines
        self.order_line._compute_tax_id()

        option_lines = []
        for option in template.sale_order_template_option_ids:
            data = self._compute_option_data_for_template_change(option)
            old_price = data.get('price_unit') or 0
            data.update({
                'price_unit': option.price_unit or old_price
            })
            option_lines.append((0, 0, data))
        self.sale_order_option_ids = option_lines

        if template.number_of_days > 0:
            self.validity_date = fields.Date.to_string(datetime.now() + timedelta(template.number_of_days))

        self.require_signature = template.require_signature
        self.require_payment = template.require_payment

        if template.note:
            self.note = template.note


class ProductNameChange(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):

            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '%s' % (name)

            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []

        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'default_code', 'product_tmpl_id', 'attribute_value_ids', 'attribute_line_ids'],
                         load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            # display only the attributes with multiple possible values on the template
            variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped(
                'attribute_id')
            variant = product.attribute_value_ids._variant_name(variable_attributes)

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                            variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                    }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                }
                result.append(_name_get(mydict))
        return result














