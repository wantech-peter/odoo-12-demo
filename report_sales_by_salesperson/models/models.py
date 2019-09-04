# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportSalesBySalesperson(models.Model):
    _name = 'report.sales.by.salesperson'

    _auto = False

    name = fields.Char("Salesman Name")
    productcode = fields.Char("Product Code")
    productname = fields.Char("Product Name")
    unit = fields.Char("Unit")
    product_qty = fields.Float("Product Quantity")
    price_total = fields.Float("Total")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_sales_by_salesperson')
        self.env.cr.execute("""
        CREATE OR REPLACE VIEW public.report_sales_by_salesperson AS 
 SELECT row_number() OVER () AS id,
    sales.name,
    pd.default_code AS productcode,
    pt.name AS productname,
    uom.name AS unit,
    sum(sol.product_uom_qty) AS product_qty,
    sum(sol.price_total) AS price_total
   FROM sale_order so
     JOIN sale_order_line sol ON so.id = sol.order_id
     JOIN res_partner cust ON so.partner_id = cust.id
     JOIN product_product pd ON sol.product_id = pd.id
     JOIN product_template pt ON pd.product_tmpl_id = pt.id
     JOIN uom_uom uom ON pt.uom_id = uom.id
     JOIN res_users ruser ON so.user_id = ruser.id
     JOIN res_partner sales ON ruser.partner_id = sales.id
  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text
  GROUP BY sales.name, pd.default_code, pt.name, uom.name;""")
