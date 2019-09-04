from itertools import groupby
from odoo import models, api


class InvoiceListSubtotal(models.AbstractModel):
    _name = 'report.invoice_list_report_subtotal.invoice_subtotal2'

    @api.model
    def _get_report_values(self, docids, data=None):
        invoice = self.env['account.invoice']
        result_vals = []
        cust_vals = []
        cust_count = {}

        values = invoice.browse(docids)
        my_values = values

        for key, item in groupby(values, lambda k: k.number_car):
            result_vals.append(dict(name=key.number, data=[
                {
                    'invoice': d,

                } for d in item]))

        for values in result_vals:
            not_int = False
            for vals in values['data']:
                try:
                    int(vals['invoice'].invoice_partner)
                except:
                    not_int = True
            values['data'] = sorted(values['data'], key=lambda x: (int(x['invoice'].invoice_partner) if not_int is False else x['invoice'].invoice_partner))

        my_values = list(my_values)
        my_values = sorted(my_values, key=lambda x: x.invoice_partner)
        for key, item in groupby(my_values, lambda k: k.invoice_partner):
            cust_vals.append(dict(name=key, data=[
                {
                    'invoice': d,

                } for d in item]))

        for values in cust_vals:
            print("len",len(values['data']))
            cust_count.update({
                values['name']: len(values['data'])
            })

        print("cust_count", cust_count)

        return {
            'docs': result_vals,
            'cust_count': cust_count
        }

