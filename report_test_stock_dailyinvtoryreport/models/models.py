# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportStockForecatDailyInvtoryreport(models.Model):
    _name = 'report.test.stock.dailyinvtoryreport'
    _auto = False
    _description = 'picking list by customer report'
    _order = 'scount asc'

    id = fields.Char(string='id')
    quotation_date = fields.Date(string='日期')
    scount = fields.Integer(string='各車總客')
    number = fields.Char(string='車輛')
    p01_qty = fields.Integer(string='(綠,白)乾支,(藍,紅)扁竹')
    p02_qty = fields.Integer(string='生根(4包/箱)')
    p03_qty = fields.Integer(string='炸支竹(20包)')
    p04_qty = fields.Integer(string='響鈴卷(箱)')
    p05_qty = fields.Integer(string='芋絲(24盒/箱)')
    p06_qty = fields.Integer(string='鮮竹')
    p07_qty = fields.Integer(string='濕竹(百好),鮮竹(一梗)')
    p08_qty = fields.Integer(string='杯裝豆漿(24杯x365ml)')
    p09_qty = fields.Integer(string='(無糖,有糖)10公升豆漿')






    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_test_stock_dailyinvtoryreport')
        self.env.cr.execute("""CREATE OR REPLACE VIEW public."report_test_stock_dailyinvtoryreport" AS
 SELECT row_number() OVER () AS id,
    x.quotation_date,
    x.scount,
    car_number_option.number,
    x.p01_qty,
    x.p02_qty,
    x.p03_qty,
    x.p04_qty,
    x.p05_qty,
    x.p06_qty,
    x.p07_qty,
    x.p08_qty,
    x.p09_qty
   FROM ( SELECT scount.quotation_date,
            scount.scount,
            scount.car_number,
            p1.p01_qty,
            p2.p02_qty,
            p3.p03_qty,
            p4.p04_qty,
            p5.p05_qty,
            p6.p06_qty,
            p7.p07_qty,
            p8.p08_qty,
            p9.p09_qty
           FROM ( SELECT so.quotation_date,
                    so.car_number,
                    count(so.id) AS scount
                   FROM sale_order so
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text
                  GROUP BY so.quotation_date, so.car_number) scount
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p01_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND (pd.default_code::text = 'A071'::text OR pd.default_code::text = 'A072'::text OR pd.default_code::text = 'A093'::text OR pd.default_code::text = 'A094'::text)
                  GROUP BY so.quotation_date, so.car_number) p1 ON scount.quotation_date = p1.quotation_date AND scount.car_number = p1.car_number
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p02_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND pd.default_code::text = 'A031e'::text
                  GROUP BY so.quotation_date, so.car_number) p2 ON p1.quotation_date = p2.quotation_date AND p1.car_number = p2.car_number
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p03_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND pd.default_code::text = 'A030'::text
                  GROUP BY so.quotation_date, so.car_number) p3 ON p1.quotation_date = p3.quotation_date AND p1.car_number = p3.car_number
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p04_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND pd.default_code::text = 'A134'::text
                  GROUP BY so.quotation_date, so.car_number) p4 ON p1.quotation_date = p4.quotation_date AND p1.car_number = p4.car_number
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p05_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND pd.default_code::text = 'A140'::text
                  GROUP BY so.quotation_date, so.car_number) p5 ON p1.quotation_date = p5.quotation_date AND p1.car_number = p5.car_number
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p06_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND pd.default_code::text = 'A036'::text
                  GROUP BY so.quotation_date, so.car_number) p6 ON p1.quotation_date = p6.quotation_date AND p1.car_number = p6.car_number
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p07_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND (pd.default_code::text = 'A036f'::text OR pd.default_code::text = 'A097f'::text)
                  GROUP BY so.quotation_date, so.car_number) p7 ON p1.quotation_date = p7.quotation_date AND p1.car_number = p7.car_number
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p08_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND pd.default_code::text = 'D013'::text
                  GROUP BY so.quotation_date, so.car_number) p8 ON p1.quotation_date = p8.quotation_date AND p1.car_number = p8.car_number
             LEFT JOIN ( SELECT so.quotation_date,
                    so.car_number,
                    sum(sol.product_uom_qty) AS p09_qty
                   FROM sale_order so
                     JOIN sale_order_line sol ON so.id = sol.order_id
                     JOIN product_product pd ON sol.product_id = pd.id
                  WHERE (so.quotation_date - now()::date) >= 1 AND so.state::text <> 'cancel'::text AND (pd.default_code::text = 'D024'::text OR pd.default_code::text = 'D025'::text)
                  GROUP BY so.quotation_date, so.car_number) p9 ON p1.quotation_date = p9.quotation_date AND p1.car_number = p9.car_number) x
     JOIN car_number_option ON x.car_number = car_number_option.id
  ORDER BY x.car_number
        """)