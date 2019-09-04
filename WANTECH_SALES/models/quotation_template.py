# -*- coding: utf-8 -*-

from odoo.addons.exist_sale_order.models import exception

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class QuotationTemplateUpdate(models.Model):
    """Quotation Template Modification"""

    _inherit = "sale.order.template"

    customer_name = fields.Many2one('res.partner', string="Customer",
                                    domain=[('customer', '=', True)])


class TemplateOrderLine(models.Model):
    _inherit = "sale.order.template.line"

    product_uom_qty = fields.Float('Quantity', required=True,
                                   digits=dp.get_precision('Product UoS'),
                                   default=0)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        res = super(SaleOrder, self).onchange_sale_order_template_id()
        if self.sale_order_template_id:
            template = self.sale_order_template_id.with_context(
                lang=self.partner_id.lang)
            self.partner_id = template.customer_name
        return res

    def redirect_to_quot_error(self, exist_order):
        action = self.env.ref(
            'sale.action_quotations_with_onboarding')
        action['views'] = [
            (self.env.ref('sale.view_order_form').id, 'form')]
        msg = _("A Sale order with this customer and same date is Exist !!.")
        raise exception.MyRedirectWarning(msg, action.id,
                                          exist_order.id,
                                          _('Go to Sale Order'))

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:

            quotation_templ = self.env['sale.order.template'].search(
                [('customer_name', '=', self.partner_id.id)], limit=1)
            if quotation_templ:

                self.update({

                    'sale_order_template_id': quotation_templ.id,
                })
            else:
                self.update({

                    'sale_order_template_id': False
                })
            if self.quotation_date:
                if self.partner_id:
                    exist_order = self.env['sale.order'].search(
                        [('partner_id', '=', self.partner_id.id),
                         ('quotation_date', '=', self.quotation_date),
                         ])
            if exist_order:
                self.redirect_to_quot_error(exist_order)
        return res

    @api.multi
    def create(self, vals_list):
        if vals_list['quotation_date']:
            if vals_list['partner_id']:
                exist_order = self.env['sale.order'].search(
                    [('partner_id', '=', vals_list['partner_id']),
                     ('quotation_date', '=', vals_list['quotation_date']),
                     ])
                if exist_order:
                    self.redirect_to_quot_error(exist_order)

        return super(SaleOrder, self).create(vals_list)

    @api.multi
    def write(self, vals):
        if 'quotation_date' in vals or 'partner_id' in vals:

            if 'quotation_date' in vals:
                new_quotation_date = vals['quotation_date']
            else:
                new_quotation_date = self.quotation_date
            if 'partner_id' in vals:
                new_partner = vals['partner_id']
            else:
                new_partner = self.partner_id.id
            if new_quotation_date:
                if new_partner:
                    exist_order = self.env['sale.order'].search(
                        [('partner_id', '=', new_partner),
                         ('quotation_date', '=', new_quotation_date),
                         ])
            # if 'state' in vals:
            #     if len(exist_order) > 1:
            #         self.redirect_to_quot_error(exist_order)
            # else:
            if exist_order:
                if exist_order.id != self.id:
                    self.redirect_to_quot_error(exist_order)

        return super(SaleOrder, self).write(vals)


class SaleOrderTemplateInherit(models.Model):
    _inherit = "sale.order.template"

    @api.model
    def create(self, values):

        values = dict(values or {})
        if values.get('sale_order_template_line_ids'):
            opt_line_ids = values['sale_order_template_line_ids']

            for line in opt_line_ids:
                line[2].update({
                    'uom_id': line[2]['product_uom_id']
                })
            values.update({
                'sale_order_template_option_ids': opt_line_ids,
            })
        return super(SaleOrderTemplateInherit, self).create(values)

    @api.multi
    def write(self, values):

        values = dict(values or {})

        if values.get('sale_order_template_line_ids'):
            opt_line_ids = values['sale_order_template_line_ids']

            for line in opt_line_ids:
                if line[0] == 0:
                    line[2].update({
                        'uom_id': line[2]['product_uom_id']
                    })
                    item_list = line[2]

                    self.update({
                        'sale_order_template_option_ids': [(0, 0, item_list)]
                    })

        return super(SaleOrderTemplateInherit, self).write(values)


class SaleOrderLIne(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:

            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id,
                                            line.product_uom_qty,
                                            product=line.product_id,
                                            partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if line.order_id.sale_order_template_id:
                line.update({
                    'price_subtotal': line.price_unit * line.product_uom_qty,
                })

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            if not self.order_id.sale_order_template_id:
                self.price_unit = self.env[
                    'account.tax']._fix_tax_included_price_company(
                    self._get_display_price(product), product.taxes_id,
                    self.tax_id, self.company_id)