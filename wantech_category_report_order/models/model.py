# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    report_order = fields.Integer(string="Report Order")


class ProductList(models.AbstractModel):
    _name = 'report.picking_list_report.report_list_product_category_car'
    _order = 'order asc'

    @api.model
    def _get_report_values(self, docids, data=None):

        query = """
            SELECT car_number,SUM(CAST(product_qty AS decimal)) as quantity,productname,report_test_stock_forecast_car.order
            FROM report_test_stock_forecast_car
            WHERE id %s
            GROUP BY car_number,productname,report_test_stock_forecast_car.order
            ORDER BY report_test_stock_forecast_car.order ASC, productname ASC, car_number
        """ % (str("in %s" % str(tuple(docids))) if len(docids) > 1 else (" = " + str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()

        products_grouped = {}
        car_numbers = []
        product_names = []
        print(data)
        data = sorted(data, key=lambda i: (i['order'] if i['order'] else 0))
        for item in data:
            car_numbers.append(item["car_number"])
            product_names.append(item["productname"])
        car_numbers = list(set(car_numbers))
        print(car_numbers)
        # car_numbers.sort()
        # print(car_numbers)
        product_names = list(set(product_names))

        for product in data:
            products_grouped[(product['productname'], product['car_number'])] = {
                'productname': product['productname'],
                'car_num': product['car_number'],
                'quantity': product['quantity'],
            }
        return {
            'doc_model': 'report.test.stock.forecast.car',
            'docs': data,
            'products_grouped': products_grouped,
            'car_numbers': car_numbers,
            'product_names': product_names,
        }


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
