from odoo import models, api


class PickingListPDF(models.AbstractModel):
    _name = 'report.picking_list_qty_pdf.report_product_list_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        query = """
                SELECT productcode,unit,productname,car_number,SUM(CAST(product_qty AS decimal))
                as total FROM report_test_stock_forecast
                WHERE id %s
                GROUP BY productname,productcode,unit,car_number;
            """ % (str("in %s" % str(tuple(docids))) if len(docids) > 1 else (" = " + str(docids[0])))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        new_data = {}
        if data:
            for item in data:
                if not item['car_number'] in new_data.keys():
                    new_data[item['car_number']] = []
                    new_data[item['car_number']].append(item)
                else:
                    new_data[item['car_number']].append(item)

        return {
            'doc_model': 'report.test.stock.forecast',
            'docs': new_data
        }




