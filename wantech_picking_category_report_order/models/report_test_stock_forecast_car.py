# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ReportTestStockForecastCar(models.Model):
    _inherit = 'report.test.stock.forecast.car'
    _auto = False

    order = fields.Integer(string="Report Order")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_test_stock_forecast_car')
        self.env.cr.execute("""CREATE OR REPLACE VIEW report_test_stock_forecast_car AS(
         SELECT row_number() OVER () AS id,
            cust.car_number,
            pd.default_code AS productcode,
            pt.name AS productname,
            sum(sm.product_qty) AS product_qty,
            uom.name AS unit,
            so.quotation_date,
            cat.name AS category,
            pt.report_order as order
           FROM stock_picking sp
             JOIN sale_order so ON sp.origin::text = so.name::text
             JOIN res_partner cust ON so.partner_id = cust.id
             JOIN car_number_option car ON so.car_number = car.id
             JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
             JOIN stock_move sm ON sp.id = sm.picking_id
             JOIN product_product pd ON sm.product_id = pd.id
             JOIN product_template pt ON pd.product_tmpl_id = pt.id
             JOIN uom_uom uom ON pt.uom_id = uom.id
             JOIN product_category cat ON pt.categ_id = cat.id
          WHERE spt.id = 1
          GROUP BY  cust.car_number, pd.default_code, pt.name, uom.name, so.quotation_date, cat.name, pt.report_order
          ORDER BY pd.default_code,cat.name,cust.car_number,pt.report_order
          )
        """)
