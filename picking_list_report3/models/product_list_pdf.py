from odoo import fields, models, api, tools, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    report_order = fields.Integer(string="Report Order")


class ProductList(models.AbstractModel):
    _name = 'report.picking_list_report.report_list_product_category_car'
    _order = 'car_number asc'

    @api.model
    def _get_report_values(self, docids, data=None):

        query = """
            SELECT car_number,SUM(CAST(product_qty AS decimal)) as quantity, productname ,unit,category, quotation_date
            FROM report_test_stock_forecast_car
            WHERE id %s
            GROUP BY car_number, productname ,unit,category, quotation_date
            ORDER BY car_number
        """ % (str("in %s"%str(tuple(docids))) if len(docids) > 1 else(" = "+str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()


        query2 = """
            SELECT car_number,SUM(CAST(product_qty AS decimal)) as quantity,productname,report_order,category,quotation_date
            FROM report_test_stock_forecast_car
            WHERE id %s
            GROUP BY car_number,productname,report_order,category,quotation_date
            ORDER BY report_order
        """ % (str("in %s"%str(tuple(docids))) if len(docids) > 1 else(" = "+str(docids[0])))
        self.env.cr.execute(query2)
        data2 = self.env.cr.dictfetchall()

        
        products_grouped = {}
        car_numbers = []
        product_names = []
        for item in data:
            car_numbers.append(item["car_number"])
        for item2 in data2:
            product_names.append((item2["productname"] , item2["report_order"]))
        car_numbers = list(set(car_numbers))
        car_numbers.sort()
        product_names = list(set(product_names))
        product_names.sort(key=lambda y: y[1])

        res_list = [product[0] for product in product_names]

        product_totals = []
        index = 0

        for product_name in res_list:
            if index not in product_totals:
                product_totals.append({"val": 0, "unit": ""})
            for product in data:
                if product['productname'] == product_name:
                    product_totals[index]["val"] = product_totals[index]["val"] + product['quantity']
                    product_totals[index]["unit"] = product['unit']
            index = index+1

        for product in data:
            products_grouped[(product['productname'],product['car_number'])] = {
                'productname': product['productname'],
                'car_num': product['car_number'],
                'quantity': product['quantity'],
                'unit': product['unit'],
            }

        return {
            'doc_model': 'report.test.stock.forecast.car',
            'docs': data,
            'products_grouped': products_grouped,
            'car_numbers': car_numbers,
            'product_names': res_list,
            'product_totals': product_totals
        }
