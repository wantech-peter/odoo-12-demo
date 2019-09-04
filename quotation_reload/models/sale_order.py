from odoo import models, fields,api, _


class QuotationReload(models.Model):
    _inherit = 'sale.order'

    is_quot_reload = fields.Boolean(string="Reload",default=False)

    def action_quotation_reload(self):

        if self.id:
            exist_line = []
            template_id = self.sale_order_template_id
            if self.order_line:

                for line in self.order_line:
                    for templ_line in template_id.sale_order_template_line_ids:
                        if templ_line.product_id.id == line.product_id.id:
                            exist_line.append(line.product_id.id)
                for templ_line in template_id.sale_order_template_line_ids:
                    if templ_line.product_id.id not in exist_line:

                        items = {
                            'product_id': templ_line.product_id.id,
                            'name': templ_line.product_id.name,
                            'product_uom_qty': templ_line.product_uom_qty,
                            'product_uom': templ_line.product_uom_id.id,
                            'price_unit': templ_line.price_unit,
                        }
                        self.is_quot_reload = True
                        self.update({
                            'order_line': [(0, 0, items)]
                        })


    def action_quotation_delete(self):

        if self.order_line:
            if self.state != 'sale':
                for line in self.order_line:
                    if line.product_uom_qty == 0:
                        line.unlink()






