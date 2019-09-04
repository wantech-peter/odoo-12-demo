# -*- coding: utf-8 -*-
from odoo import http

# class WantechSale(http.Controller):
#     @http.route('/wantech_sale/wantech_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wantech_sale/wantech_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wantech_sale.listing', {
#             'root': '/wantech_sale/wantech_sale',
#             'objects': http.request.env['wantech_sale.wantech_sale'].search([]),
#         })

#     @http.route('/wantech_sale/wantech_sale/objects/<model("wantech_sale.wantech_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wantech_sale.object', {
#             'object': obj
#         })