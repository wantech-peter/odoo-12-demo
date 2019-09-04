from odoo import models, api, _


class ProductList(models.AbstractModel):
    _name = 'report.product_category_list_pdf.report_list_product_category'

    @api.model
    def _get_report_values(self, docids, data=None):

        query = """
            SELECT car_number,SUM(CAST(product_qty AS decimal)) as quantity,productname
            FROM report_test_stock_forecast
            WHERE category = '1 乾貨' and
            id %s
            GROUP BY car_number,productname;
        """ % (str("in %s"%str(tuple(docids))) if len(docids) > 1 else(" = "+str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        
        products_grouped = {}
        for product in data:
            products_grouped[product['productname'],product['car_number']]  ={
                'productname': product['productname'],
                'car_num': product['car_number'],
                'quantity': product['quantity'],

            }
        

    


        return {
            'doc_model': 'report.test.stock.forecast',
            'docs': data,
            'products_grouped': products_grouped
        }
