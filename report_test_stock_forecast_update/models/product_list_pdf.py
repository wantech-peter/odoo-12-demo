from odoo import models, api


class ProductList(models.AbstractModel):
    _name = 'report.report_test_stock_forecast_update.report_customer'

    # _order = 'car_number asc'

    @api.model
    def _get_report_values(self, docids, data=None):
        query2 = """
            SELECT custname,SUM(CAST(product_qty AS decimal)) as quantity,productname,unit,car_number,category,quotation_date
            FROM report_test_stock_forecast_customer
            WHERE id %s
            GROUP BY custname,productname,unit,car_number,category,quotation_date
            ORDER BY car_number
        """ % (str("in %s" % str(tuple(docids))) if len(docids) > 1 else (
                " = " + str(docids[0])))
        self.env.cr.execute(query2)
        data = self.env.cr.dictfetchall()
        query3 = """
            SELECT custname,SUM(CAST(product_qty AS decimal)) as quantity,productname,report_order,quotation_date
            FROM report_test_stock_forecast_customer
            WHERE id %s
            GROUP BY custname,productname,report_order,quotation_date
            ORDER BY report_order
        """ % (str("in %s" % str(tuple(docids))) if len(docids) > 1 else (
                " = " + str(docids[0])))
        self.env.cr.execute(query3)
        data2 = self.env.cr.dictfetchall()
        query4 = """
            SELECT SUM(CAST(product_qty AS decimal)) as quantity,productname,car_number
            FROM report_test_stock_forecast_customer
            WHERE id %s
            GROUP BY car_number, productname
        """ % (str("in %s" % str(tuple(docids))) if len(docids) > 1 else (
                " = " + str(docids[0])))
        self.env.cr.execute(query4)
        data3 = self.env.cr.dictfetchall()
        products_grouped = {}
        car_numbers = []
        customer_names = []
        product_names = []
        car_totals = {}

        for item in data:
            customer_names.append(item["custname"])
            car_numbers.append(item["car_number"])
        customer_names = list(set(customer_names))
        customer_names.sort()
        car_numbers = list(set(car_numbers))
        car_numbers.sort()

        for item2 in data2:
            product_names.append((item2["productname"], item2["report_order"]))
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
                    product_totals[index]["val"] = product_totals[index][
                                                       "val"] + product[
                                                       'quantity']
                    product_totals[index]["unit"] = product['unit']
            index = index + 1

        for product in data:
            products_grouped[(product['car_number'], product['productname'],
                              product['custname'])] = {
                'productname': product['productname'],
                'custname': product['custname'],
                'car_num': product['car_number'],
                'quantity': product['quantity'],
                'unit': product['unit'],
            }
        for item in data3:
            if item:
                if item['car_number'] in car_totals.keys():
                    car_totals[item['car_number']][item['productname']] = (item['quantity'] if item['quantity'] else 0.0)
                else:
                    car_totals[item['car_number']] = {}
                    car_totals[item['car_number']][item['productname']] = (item['quantity'] if item['quantity'] else 0.0)
        aaaaa = products_grouped
        return {
            'doc_model': 'report.test.stock.forecast.customer',
            'docs': data,
            'products_grouped': products_grouped,
            'car_numbers': car_numbers,
            'customer_names': customer_names,
            'product_names': res_list,
            'product_totals': product_totals,
            'car_totals': car_totals
        }
