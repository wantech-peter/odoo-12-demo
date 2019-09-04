
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    is_button_visible = fields.Boolean(string="Visible")

    @api.onchange('is_button_visible')
    @api.depends('is_button_visible')
    def onchange_is_button_visible(self):
        print("self.picking_type_code ",self.picking_type_code )

        if self.env.user.company_id.id != 2 and self.state == 'draft' and self.picking_type_code in ['outgoing','internal']:
            self.is_button_visible = True
        else:
            self.is_button_visible = False

    @api.multi
    def add_products(self):

        query = """
                select id,product_id,quantity,company_id,quantity as forecast
                from report_stock_forecast rp 
                where company_id = 2 and quantity < 0
                """

        self._cr.execute(query)
        results = self._cr.dictfetchall()
        for value in results:
            product = self.env['product.product'].browse(value['product_id'])
            items = {
                'name': product.name,
                'product_uom': product.uom_id,
                'product_uom_qty': abs(value['forecast']),
                'location_id': self.location_id,
                'picking_type_id': self.picking_type_id,
                'location_dest_id': self.location_dest_id,
                'product_id': product.id,
            }
            self.update({
                'move_ids_without_package': [(0, 0, items)]
            })

    @api.multi
    def create_order(self):

        picking_obj = self.env['stock.picking']
        picking_move_obj = self.env['stock.move']
        picking_type_id = self.env['stock.picking.type'].sudo().search([
            ('default_location_src_id.usage', '=', 'transit'),
            ('default_location_src_id.company_id', '=', False)
        ])

        if not picking_type_id:
            raise UserError(_('Please define a Operation Type with Transit Location as Default source location !'))

        location_id = picking_type_id.default_location_src_id
        pick_id = picking_obj.sudo().create({
            'scheduled_date': self.scheduled_date,
            'picking_type_id': picking_type_id.id,
            'location_id': location_id.id,
            'move_type': 'direct',
            'location_dest_id': 20,
            'company_id': 2,
        })
        for value in self.move_ids_without_package:
            picking_move_obj.sudo().create({
                'name': value.product_id.name,
                'product_uom': value.product_uom.id,
                'product_uom_qty': value.quantity_done,
                'location_id': pick_id.location_id.id,
                'company_id': 2,
                'picking_id': pick_id.id,
                'picking_type_id': pick_id.picking_type_id.id,
                'location_dest_id': pick_id.location_dest_id.id,
                'product_id': value.product_id.id,
            })