
from odoo import models, api, fields, _


class BatchUpdatePrice(models.Model):
    _name = 'batch.update.wizard'

    product_id = fields.Many2one('product.product', String='Product', required=True)
    price = fields.Float('Price', required=True)

    @api.multi
    def batch_update(self):
        active_ids = self._context.get('active_ids')
        order_ids = self.env['sale.order.template'].browse(active_ids)
        product_id = self.product_id
        for line in order_ids:
            if product_id.id in line.sale_order_template_line_ids.mapped('product_id').ids:
                for line2 in line.sale_order_template_line_ids:
                    if line2.product_id.id == product_id.id:
                        line2.update({
                            'price_unit': self.price,
                        })
            else:
                line.sale_order_template_line_ids.create({
                    'product_id': product_id.id,
                    'name': product_id.name,
                    'price_unit': self.price,
                    'sale_order_template_id': line.id,
                    'product_uom_qty': 0,
                    'product_uom_id': product_id.uom_id.id
                })

