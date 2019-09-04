from odoo import models, fields, api


class AutoQuotations(models.Model):
    _inherit = "sale.order.template"

    auto_generate = fields.Boolean('Auto Generation')


class GenerateQuotations(models.Model):
    _name = "quotation.auto.generate"
    _inherit = "sale.order.template"

    @api.model
    def auto_generate_quotations(self):

        template_obj = self.env['sale.order.template'].search([('auto_generate', '=', True)])
        for obj in template_obj:
            lines = []
            for line in obj.sale_order_template_line_ids:
                lines.append((0, 0,
                              {
                                  'product_id': line.product_id.id,
                                  'name': line.name,
                                  'product_uom_qty': line.product_uom_qty,
                                  'price_unit': line.price_unit,
                              }))
            try:
                self.env['sale.order'].create({
                    'partner_id': obj.customer_name.id,
                    'sale_order_template_id': obj.id,
                    'order_line': lines,
                })
            except Exception as e:
                continue


class SaleOrderInternalNotes(models.Model):
    _inherit = 'sale.order'

    """Internal Notes and Customer Number in Sale Order """

    payment_internal_note = fields.Text(string="Internal Note", compute='customerdetails')
    customer_number = fields.Char(string='Customerdetails', compute='customerdetails')
    street1 = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city_name = fields.Char(related='partner_id.city')
    state_id1 = fields.Char(related='partner_id.state_id.name')
    zip1 = fields.Char(related='partner_id.zip')
    country_id1 = fields.Char(related='partner_id.country_id.name')

    @api.multi
    @api.onchange('partner_id')
    def customerdetails(self):
        self.ensure_one()
        partner = self.env['res.partner'].browse(self.partner_id.id)
        self.payment_internal_note = partner.comment
        self.customer_number = partner.partner_number
        # try:
        # self.customer_address = "\n".join([partner.street, partner.city + " " + partner.state_id.code + " " + partner.zip, partner.country_id.name])
        # except Exception as e:
        #     return
