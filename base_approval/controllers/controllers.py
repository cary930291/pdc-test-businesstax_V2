# -*- coding: utf-8 -*-
from odoo import http

# class RtApprovalRecords(http.Controller):
#     @http.route('/rt_approval_records/rt_approval_records/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_approval_records/rt_approval_records/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_approval_records.listing', {
#             'root': '/rt_approval_records/rt_approval_records',
#             'objects': http.request.env['rt_approval_records.rt_approval_records'].search([]),
#         })

#     @http.route('/rt_approval_records/rt_approval_records/objects/<model("rt_approval_records.rt_approval_records"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_approval_records.object', {
#             'object': obj
#         })
