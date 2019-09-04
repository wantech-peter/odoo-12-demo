# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportStockForecatByCustomerNumber(models.Model):
    _name = 'report.test.stock.forecast.customer'
    _auto = False
    _description = 'picking list by customer report'
    _order = 'custno asc'

    id = fields.Char(string='id')

    custno = fields.Char(string='custno')
    custname = fields.Char(string='custname')
    car_number = fields.Integer(string='car_number')
    productcode = fields.Char(string='productcode')
    productname = fields.Char(string='productname')
    report_order = fields.Integer(string='report_order')
    product_qty = fields.Char(string='product_qty')

    unit = fields.Char(string='unit')
    quotation_date = fields.Date(string='quotation_date')
    category = fields.Char(string='category')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_test_stock_forecast_customer')
        self.env.cr.execute("""CREATE OR REPLACE VIEW public.report_test_stock_forecast_customer AS
             SELECT row_number() OVER () AS id,
                cust.ref AS custno,
                cust.name AS custname,
                cust.car_number AS car_number,
                pd.default_code AS productcode,
                pt.name AS productname,
                pt.report_order,
                sum(sm.product_qty) AS product_qty,
                uom.name AS unit,
                so.quotation_date,
                cat.name AS category
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
              WHERE (spt.id = 1 OR spt.id = 6) AND (so.quotation_date - now()::date) >= '-2'::integer AND sp.state::text <> 'cancel'::text
              GROUP BY cust.ref, cust.name, cust.car_number, pd.default_code, pt.name, uom.name, so.quotation_date, cat.name, pt.report_order
        """)