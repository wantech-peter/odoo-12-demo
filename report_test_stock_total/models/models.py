# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportStockTotal(models.Model):
    _name = 'report.test.stock.total'
    _auto = False
    _description = 'Stock Total Report'
    order = 'product_qty asc'

    id = fields.Char(string='id')
    productcode = fields.Char(string='productcode')
    productname = fields.Char(string='productname')
    product_qty = fields.Integer(string='product_qty')
    unit = fields.Char(string='unit')
    quotation_date = fields.Char(string='quotation_date')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_test_stock_total')
        self.env.cr.execute("""CREATE OR REPLACE VIEW report_test_stock_total AS(
             SELECT row_number() OVER () AS id,
                pd.default_code AS productcode,
                pt.name AS productname,
                sum(sm.product_uom_qty) AS product_qty,
                uom.name AS unit,
                (sm.date::date + ((1 || ' days'::text)::interval))::date AS quotation_date
               FROM stock_move sm
                 JOIN stock_move_line sml ON sm.id = sml.move_id
                 JOIN product_product pd ON sm.product_id = pd.id
                 JOIN product_template pt ON pd.product_tmpl_id = pt.id
                 JOIN uom_uom uom ON pt.uom_id = uom.id
              WHERE (sm.date::date - now()::date) >= 0 AND sm.location_id = 12 AND sm.picking_type_id = 1
              GROUP BY (sm.date::date), pd.default_code, pt.name, uom.name
              )
        """)