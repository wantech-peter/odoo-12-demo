# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportStockoutInCat19(models.Model):
    _name = 'report.stockout.in.cat19'

    _auto = False

    custno = fields.Char("Customer No")
    custname = fields.Char("Customer Name")
    customer_type = fields.Char("Customer Type")
    productcode = fields.Char("Product Code")
    productname = fields.Char("Product Name")
    price_unit = fields.Float("Price")
    product_qty = fields.Float("Quantity")
    unit = fields.Char("Unit")
    quotation_date = fields.Date("Quotation Date")
    category = fields.Char("Category")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_stockout_in_cat19')
        self.env.cr.execute("""
        CREATE OR REPLACE VIEW public.report_stockout_in_cat19 AS 
 SELECT row_number() OVER () AS id,
    cust.ref AS custno,
    cust.name AS custname,
    coption.type AS customer_type,
    pd.default_code AS productcode,
    pt.name AS productname,
    stempline.price_unit,
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
     JOIN sale_order_template stemp ON stemp.customer_name = so.partner_id
     JOIN sale_order_template_line stempline ON stemp.id = stempline.sale_order_template_id AND stempline.product_id = pd.id
     LEFT JOIN customer_type_option coption ON cust.customer_type = coption.id
  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND pt.categ_id = 19
  GROUP BY car.number, cust.ref, cust.name, coption.type, cust.car_number, pd.default_code, pt.name, uom.name, so.quotation_date, cat.name, stempline.price_unit;
        """)
