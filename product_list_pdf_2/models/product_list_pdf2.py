from odoo import models, api, _


class ProductList(models.AbstractModel):
    _name = 'report.product_list_pdf.report_list_product'

    @api.model
    def _get_report_values(self, docids, data=None):
        query = """
            SELECT productcode,unit,productname,SUM(CAST(product_qty AS decimal))
            as total, dndate FROM report_test_stock_forecast
            WHERE id %s
            GROUP BY category,productname,productcode,unit,dndate ORDER BY category,productname,productcode;
        """ % (str("in %s"%str(tuple(docids))) if len(docids) > 1 else(" = "+str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        return {
            'doc_model': 'report.test.stock.forecast',
            'docs': data
        }


class ProductListPk(models.AbstractModel):
    _name = 'report.product_list_pdf.report_list_product_pk'

    @api.model
    def _get_report_values(self, docids, data=None):
        query = """
            SELECT productcode,unit,productname,SUM(CAST(product_qty AS decimal))
            as total, dndate FROM report_test_stock_forecast
            WHERE id %s
            GROUP BY category,productname,productcode,unit,dndate ORDER BY category,productname,productcode;
        """ % (str("in %s"%str(tuple(docids))) if len(docids) > 1 else(" = "+str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        return {
            'doc_model': 'report.test.stock.forecast',
            'docs': data
        }


class ProductListKb(models.AbstractModel):
    _name = 'report.product_list_pdf.report_list_product_kb'

    @api.model
    def _get_report_values(self, docids, data=None):
        query = """
            SELECT productcode,unit,productname,SUM(CAST(product_qty AS decimal))
            as total, dndate FROM report_test_stock_forecast
            WHERE id %s
            GROUP BY category,productname,productcode,unit,dndate ORDER BY category,productname,productcode;
        """ % (str("in %s"%str(tuple(docids))) if len(docids) > 1 else(" = "+str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        return {
            'doc_model': 'report.test.stock.forecast',
            'docs': data
        }



class ProductList2(models.AbstractModel):
    _name = 'report.product_list_pdf.report_list_product2'

    @api.model
    def _get_report_values(self, docids, data=None):
        query = """
            SELECT productcode,unit,productname,SUM(CAST(product_qty AS decimal))
            as total, dndate FROM report_test_stock_forecast
            WHERE id %s
            GROUP BY category,productname,productcode,unit,dndate ORDER BY category,productname,productcode;
        """ % (str("in %s"%str(tuple(docids))) if len(docids) > 1 else(" = "+str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        return {
            'doc_model': 'report.test.stock.forecast',
            'docs': data
        }