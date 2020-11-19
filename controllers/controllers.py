# -*- coding: utf-8 -*-
# from odoo import http


# class Parkinglot(http.Controller):
#     @http.route('/parkinglot/parkinglot/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/parkinglot/parkinglot/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('parkinglot.listing', {
#             'root': '/parkinglot/parkinglot',
#             'objects': http.request.env['parkinglot.parkinglot'].search([]),
#         })

#     @http.route('/parkinglot/parkinglot/objects/<model("parkinglot.parkinglot"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('parkinglot.object', {
#             'object': obj
#         })
