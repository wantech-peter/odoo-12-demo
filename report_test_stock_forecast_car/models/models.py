# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportStockForecatByCarNumber(models.Model):
    _name = 'report.test.stock.forecast.car'
    _auto = False
    _description = 'picking list by carnumber report'

    id = fields.Char(string='id')

    car_number = fields.Char(string='car_number')
    productcode = fields.Char(string='productcode')
    productname = fields.Char(string='productname')
    product_qty = fields.Char(string='product_qty')
    unit = fields.Char(string='unit')
    quotation_date = fields.Char(string='quotation_date')
    category = fields.Char(string='category')
    report_order = fields.Integer(string='product_qty')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_test_stock_forecast_car')
        self.env.cr.execute("""CREATE OR REPLACE VIEW public.report_test_stock_forecast_car AS
 SELECT row_number() OVER () AS id,
    car.number::integer AS car_number,
    pd.default_code AS productcode,
    pt.name AS productname,
    pt.report_order,
    sum(sol.product_uom_qty) AS product_qty,
    uom.name AS unit,
    so.quotation_date,
    cat.name AS category
   FROM sale_order so
     JOIN sale_order_line sol ON so.id = sol.order_id
     JOIN res_partner cust ON so.partner_id = cust.id
     JOIN car_number_option car ON so.car_number = car.id
     JOIN product_product pd ON sol.product_id = pd.id
     JOIN product_template pt ON pd.product_tmpl_id = pt.id
     JOIN uom_uom uom ON pt.uom_id = uom.id
     JOIN product_category cat ON pt.categ_id = cat.id
  WHERE (so.quotation_date - now()::date) >= '-1'::integer AND so.state::text <> 'cancel'::text
  GROUP BY car.number, pd.default_code, pt.name, uom.name, so.quotation_date, cat.name, pt.report_order
  ORDER BY car.number, cat.name, pd.default_code
        """)
