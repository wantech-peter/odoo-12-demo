# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api


class PickingCarFavouriteWizard(models.TransientModel):
    _name = 'picking.car.favourite.wizard'

    filter_id = fields.Many2one('ir.filters', string="Filter",
                                domain=[('model_id', '=', 'report.test.stock.forecast.car'), ], required=True)
    sort_by = fields.Text(string="Sort By", readonly=True)

    @api.depends('filter_id')
    @api.onchange('filter_id')
    def filter_id_change(self):
        if not self.filter_id.id or self.filter_id.sort == '[]':
            return
        sort_o = ""
        sort_fields = self.filter_id.sort.split(',')
        for sort in sort_fields:
            sort_o += (sort.replace('-', '') + " Descending \n") if sort[0] == '-' else (sort + " Ascending\n")
        self.sort_by = sort_o

    def print_report(self):
        group = [
            'car_number'
            , 'productcode'
            , 'productname'
            , 'unit'
            , 'category'
            , 'order']
        ctxt = self.filter_id.context.split("'group_by': [")[1].split(']')[0].split(',')
        ctxt = ctxt[0]
        print(ctxt)
        index = 0
        for ct in ctxt:
            try:
                temp = group.index(ct)
                group[index], group[temp] = group[temp], group[index]
            except Exception as e:
                continue
        group[group.index('order')] = 'report_test_stock_forecast_car.order'
        GROUP_BY = "GROUP BY "
        for gr in group:
            GROUP_BY += gr + ","
        GROUP_BY = GROUP_BY[:len(GROUP_BY) - 1]
        sorts = self.filter_id.sort.replace('[', '').replace(']', '').split(',')
        ORDER_BY = ""
        if len(sorts) > 1:
            ORDER_BY = """
            ORDER BY
            """
            for so in sorts:
                ORDER_BY += (((so[1:]) + " DESC,") if re.match("-", so) else (so + " ASC,"))
            ORDER_BY = ORDER_BY[:len(ORDER_BY) - 1]
        filter_ = self.filter_id.domain[1:len(self.filter_id.domain) - 1].split('],')
        WHERE = """
                """
        if len(filter_) > 0:
            WHERE = """
            WHERE 
            """
            relationals = ""
            if re.match('&', filter_[0]) or re.match('\|', filter_[0]) or re.match('in', filter_[0]) or re.match(
                    'not in', filter_[0]) or re.match('ilike', filter_[0]):
                relationals = filter_[0]
                filter_ = filter_[1:]
            if len(relationals) > 0:
                relationals.replace('&', ' AND ').replace('\|', ' OR ')
            index = 0
            no_index = False
            for fil in filter_:
                filt = fil.replace('[', '').replace(']', '').replace('"', "'").split(',')
                print(filt)
                filt[1] = filt[1].replace("'", '').replace(' ', '')
                WHERE += (filt[0].replace("'", '').replace(' ', '') + ' ' + filt[1] + ' ' + filt[2]) if not filt[
                                                                                                                1] == "ilike" else (
                        filt[0].replace(' ', '').replace("'", '') + ' ' + filt[1] + ' ' + filt[2][
                                                                                          :len(filt[2]) - 1] + "%'")
                if index < len(relationals) and len(relationals) > 0:
                    WHERE += " " + relationals[index]

                else:
                    WHERE += " AND "
                    no_index = True
            if no_index:
                WHERE = WHERE[:len(WHERE) - 5]
        WHERE += '\n'
        query = """
        SELECT 
        car_number,
        productcode,
        productname,
        SUM(product_qty) AS total,
        unit,
        category,
        report_test_stock_forecast_car.order FROM report_test_stock_forecast_car
        """ + WHERE + GROUP_BY + ORDER_BY
        cr = self._cr
        cr.execute(query)
        data = cr.dictfetchall()
        print(query)
        return {
            'context': self._context,
            'data': {
                'data': data
            },
            'type': 'ir.actions.report',
            'report_name': "wantech_picking_category_report_order.favourite_pdf",
            'report_type': 'qweb-pdf',
            'report_file': "wantech_picking_category_report_order.favourite_pdf",
            'name': "Category List",
        }
