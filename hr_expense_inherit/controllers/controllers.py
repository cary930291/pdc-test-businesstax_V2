# -*- coding: utf-8 -*-
from odoo import http

# class RtHrExpense(http.Controller):
#     @http.route('/rt_hr_expense/rt_hr_expense/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_hr_expense/rt_hr_expense/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_hr_expense.listing', {
#             'root': '/rt_hr_expense/rt_hr_expense',
#             'objects': http.request.env['rt_hr_expense.rt_hr_expense'].search([]),
#         })

#     @http.route('/rt_hr_expense/rt_hr_expense/objects/<model("rt_hr_expense.rt_hr_expense"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_hr_expense.object', {
#             'object': obj
#         })
