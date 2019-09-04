from odoo import models, fields, _
from odoo.exceptions import UserError

from itertools import groupby
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from operator import itemgetter



class MassPicking(models.TransientModel):
    _name = 'mass.picking.orders'

    def validate_picking(self):
        active_pickings = self._context.get('active_ids')
        pickings = self.env['stock.picking'].browse(active_pickings).filtered(lambda picking: picking.state not in ('cancel', 'done'))
        for my_pickings in pickings:
            self.ensure_one()
            if not my_pickings.move_lines and not my_pickings.move_line_ids:
                raise UserError(_('Please add some items to move.'))

            # If no lots when needed, raise error
            picking_type = my_pickings.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                                     my_pickings.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(
                float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in
                my_pickings.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                raise UserError(_(
                    'You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = my_pickings.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0,
                                                   precision_rounding=line.product_uom_id.rounding)
                    )

                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            raise UserError(
                                _('You need to supply a Lot/Serial number for product %s.') % product.display_name)

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({
                'pick_ids': [(4, p.id) for p in pickings],
            })
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }



# class MassPicking(models.TransientModel):
#     _name = 'mass.picking.orders'

#     def validate_picking(self):
#         active_pickings = self._context.get('active_ids')
#         my_pickings = self.env['stock.picking'].browse(active_pickings).filtered(lambda picking: picking.state not in ('cancel', 'done'))

#         picking_to_backorder = self.env['stock.picking']
#         picking_without_qty_done = self.env['stock.picking']
#         for picking in my_pickings:
#             if all([x.qty_done == 0.0 for x in picking.move_line_ids]):
#                 # If no lots when needed, raise error
#                 picking_type = picking.picking_type_id
#                 if (picking_type.use_create_lots or picking_type.use_existing_lots):
#                     for ml in picking.move_line_ids:
#                         if ml.product_id.tracking != 'none':
#                             raise UserError(_('Some products require lots/serial numbers.'))
#                 # Check if we need to set some qty done.
#                 picking_without_qty_done |= picking
#             elif picking._check_backorder():
#                 picking_to_backorder |= picking
#             else:
#                 picking.action_done()
#         self.write({'state': 'done'})
#         if picking_without_qty_done:
#             view = self.env.ref('stock.view_immediate_transfer')
#             wiz = self.env['stock.immediate.transfer'].create({
#                 'pick_ids': [(4, p.id) for p in picking_without_qty_done],
#                 'pick_to_backorder_ids': [(4, p.id) for p in picking_to_backorder],
#             })
#             return {
#                 'name': _('Immediate Transfer?'),
#                 'type': 'ir.actions.act_window',
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'stock.immediate.transfer',
#                 'views': [(view.id, 'form')],
#                 'view_id': view.id,
#                 'target': 'new',
#                 'res_id': wiz.id,
#                 'context': self.env.context,
#             }
#         if picking_to_backorder:
#             return picking_to_backorder.action_generate_backorder_wizard()
