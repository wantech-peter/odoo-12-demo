# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportStockForecat(models.Model):
    _name = 'report.test.stock.forecast'
    _auto = False
    _description = 'Stock test Forecast Report'
    _order = 'productcode asc, custname asc'

    id = fields.Char(string='id')

    custno = fields.Char(string='custno')
    custname = fields.Char(string='custname')
    car_number = fields.Char(string='car_number')
    customer_stopnum = fields.Char(string='customer_stopnum')
    sono = fields.Char(string='sono')
    dnno = fields.Char(string='dnno')
    dndate = fields.Char(string='dndate')
    productcode = fields.Char(string='productcode')
    productname = fields.Char(string='productname')
    product_qty = fields.Integer(string='product_qty')
    unit = fields.Char(string='unit')
    sodate = fields.Char(string='sodate')
    category = fields.Char(string='Category')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_test_stock_forecast')
        self.env.cr.execute("""CREATE OR REPLACE VIEW public.report_test_stock_forecast AS
 SELECT row_number() OVER () AS id,
    cust.partner_number AS custno,
    cust.name AS custname,
    car.number::integer AS car_number,
    cust.customer_stopnum,
    so.name AS sono,
    so.name AS dnno,
    so.quotation_date::timestamp without time zone AS dndate,
    pd.default_code AS productcode,
    pt.name AS productname,
    sol.product_uom_qty AS product_qty,
    uom.name AS unit,
    so.quotation_date AS sodate,
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
  ORDER BY pd.default_code, cat.name
        """)