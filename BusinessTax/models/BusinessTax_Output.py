# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

import time
import datetime
from datetime import date
from datetime import datetime, date, time ,timedelta
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.tools import email_split, float_is_zero

from odoo.addons import decimal_precision as dp


class BusinessTaxBook(models.Model):
    _name = 'businesstax.book'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Book Master Data"

    name = fields.Char(string='Name', index=True, required=True, track_visibility='always')
    vat_name = fields.Many2one('businesstax.name', string='Vat Name', store=True, track_visibility='always')
    vat_code = fields.Char(string='Vat Code', index=True, required=True, size=8, track_visibility='always')

    method = fields.Many2one('businesstax.method', string='Method', store=True, track_visibility='always')
    year = fields.Many2one('businesstax.year', string='Year', store=True, track_visibility='always')
    period_start = fields.Many2one('businesstax.period', string='Period start', store=True, track_visibility='always')
    period_end = fields.Many2one('businesstax.period', string='Period End', store=True, track_visibility='always')
    certificate_category = fields.Many2one('businesstax.certificate.category', string='Certificate Category',
                                           store=True, track_visibility='always')
    vat_declare_code = fields.Many2one('businesstax.vat.declare.code', string='Vat Declare Code', store=True, track_visibility='always')
    profix = fields.Many2one('businesstax.profix', string='Profix', store=True, track_visibility='always')
    invoice_begin = fields.Char(string='Invoice Begin', store=True, size=8, track_visibility='always')
    invoice_end = fields.Char(string='Invoice End', store=True, size=8, track_visibility='always')
    profix_type = fields.Many2one('businesstax.profix.type', string='Profix Type', store=True, track_visibility='always')
    invoice_next = fields.Many2one('businesstax.book', string='Invoice Next', store=True, track_visibility='always')
    invoice_now = fields.Char(string='Invoice Now', store=True, track_visibility='always')
    status = fields.Many2one('businesstax.status', string='Status', store=True, track_visibility='always')
    invoice_lastdate = fields.Date(string='Invoice Now', store=True, track_visibility='always')


class BusinessTaxInvoice(models.Model):
    _name = 'businesstax.invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Invoice Master Data"

    @api.depends('vat_name')
    @api.multi
    def _set_value(self):
        self.tax_code = self.vat_name.tax_code
        self.vat_code = self.vat_name.vat_code

    name = fields.Char(string='Name', index=True, required=True, track_visibility='always')
    certificate_category = fields.Many2one('businesstax.certificate.category', string='Certificate Category',
                                           store=True, track_visibility='always')
    invoice_date = fields.Date(string='Invoice Date', store=True, track_visibility='always')
    sales_amount = fields.Integer(string='Sales Amount', store=True, track_visibility='always')
    tax_amount = fields.Integer(string='Tax Amount', store=True, track_visibility='always')
    partner = fields.Many2one('res.partner', string='Partner',
                              store=True, track_visibility='always')
    vat_code_partner = fields.Char(string='Vat Code Partner', store=True, track_visibility='always')
    book = fields.Many2one('businesstax.book', string='Book', store=True, track_visibility='always')
    type = fields.Many2one('businesstax.type', string='Type', store=True, track_visibility='always')
    tax_code_type = fields.Many2one('businesstax.tax.code.type', string='Tax Code Type', store=True, track_visibility='always')
    declare_deduction = fields.Many2one('businesstax.declare.deduction', string='Declare Deduction', store=True, track_visibility='always')
    vat_declare_code = fields.Many2one('businesstax.vat.declare.code', string='Vat Declare Code', store=True, track_visibility='always')
    year = fields.Many2one('businesstax.year', string='Year', store=True, track_visibility='always')
    period = fields.Many2one('businesstax.period', string='Period', store=True, track_visibility='always')
    through_custom = fields.Many2one('businesstax.through.custom', string='Through Custom', store=True, track_visibility='always')
    vat_name = fields.Many2one('businesstax.name', string='Vat Name', store=True, track_visibility='always')
    tax_code = fields.Char(string='Tax Code', store=True,compute="_set_value", track_visibility='always')
    vat_code = fields.Char(string='Vat Code', store=True,compute="_set_value", track_visibility='always')
    profix = fields.Many2one('businesstax.profix', string='Profix', store=True, track_visibility='always')
#    invoice_no = fields.Char(string='Invoice No', index=True, required=True, size=8, track_visibility='always')
    invoice_no = fields.Char(string='Invoice No', index=True, size=8, track_visibility='always')
    declare_year = fields.Many2one('businesstax.year', string='Year', store=True, track_visibility='always')
    declare_period = fields.Many2one('businesstax.period', string='Period', store=True, track_visibility='always')
    customs_collection_no = fields.Char(string='Customs Collection no', index=True, size=14, track_visibility='always')
    tax_base = fields.Integer(string='Tax Base', store=True, track_visibility='always')
    date_print = fields.Date(string='Print Date', readonly=True, copy=False, track_visibility='always')
    user_id = fields.Many2one('res.users', string='Print User', readonly=True, copy=False, track_visibility='always')

    state = fields.Selection([
        ('printed', 'Printed'),
        ('open', 'Open'),
    ], string='Status', index=True, readonly=True, default='open', copy=False,
        help=" * The 'Printed' status is used when a user is print Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user print the invoice.\n"
        , track_visibility='always')

    @api.model
    def _get_year(self, in_year):
        con_year = self.env['businesstax.year'].search([])
        for line in con_year:
            if int(line.name) == in_year:
                return line.id
        return False

    @api.onchange('type', 'certificate_category')
    def _set_vat_declare_code(self):
        if self.type and self.certificate_category:
            self.vat_declare_code = ''
            mapping = self.env['businesstax.vat.declare.mapping'].search([])
            for line in mapping:
                if (self.type == line.type and self.certificate_category == line.certificate_category):
                    self.vat_declare_code = line.vat_declare_code.id
                    break

    @api.onchange('name', 'certificate_category', 'invoice_date')
    def _set_profix(self):
        if self.name and self.certificate_category.name and self.invoice_date and self.type.name:
            _inp_date = str(self.invoice_date)
            _inp_year = str(int(_inp_date[0:4]) - 1911)
            _inp_mon = _inp_date[5:7]
            self.year = ''
            self.period = ''
            _inp_year = int(self.invoice_date.year) - 1911
            con_year = self.env['businesstax.year'].search([])
            for line in con_year:
                if int(line.name) == _inp_year:
                    self.year = line.id
                    break
            con_mon = self.env['businesstax.period'].search([])
            for line in con_mon:
                if int(line.name) == self.invoice_date.month:
                    self.period = line.id
                    break
            if not self.year.id:
                raise ValidationError(_('找不到對應的年度主檔,請確認發票年度是否正確!!\r\n' + str(_inp_year)))
            if not self.period.id:
                raise ValidationError(_('找不到對應的月份主檔,請確認發票月份是否正確!!\r\n' + str(self.invoice_date.month)))
            if self.type.id in [4, 5]:  # 銷項(4,5)才有發票本
                _book = self.env['businesstax.book'].search([])
            else:  # 進項(1,2,3)對字軌
                if self.name:
                    _profix = self.env['businesstax.profix'].search([])
                    _inp_name = self.name[0:2]
                    for line in _profix:
                        if str(_inp_name) == str(line.name) and str(_inp_year) == str(line.year.name) and (
                                int(_inp_mon) >= int(line.period_start.name) and int(_inp_mon) <= int(
                            line.period_end.name)):
                            self.profix = line.id
                            break
                    if not self.profix:
                        if self.certificate_category.id in [1, 2, 3, 4, 5, 6, 7]:
                            raise ValidationError(_('找不到對應的字軌主檔資料,請確認字軌主檔與申報資料是否符合!!\r\n'))


    @api.onchange('name')
    def _set_invoice_date(self):
        if not self.invoice_no:
            if self.name:
                self.invoice_no = self.name[2:10]


    @api.multi
    def export_invoice_textfile(self):
        context = dict(self._context or {})
        values = []
        sel_ids = ''
        active_ids = context.get('active_ids', []) or []
        for record in self.env['businesstax.invoice'].browse(active_ids):
            if sel_ids == '':
                sel_ids = str(record.id)
            else:
                sel_ids += ',' + str(record.id)
            if record.state == 'open':
                record.update({
                    'state': 'printed',
                    'date_print': fields.Date.context_today(self),
                    'user_id': self.env.user,
                })
        _url = '/make/txt?invoice_ids=%s' % sel_ids

        client_action = {
            'type': 'ir.actions.act_url',
            'name': "Make txt",
            'target': 'new',
            'url': _url,
        }
        return client_action


    @api.multi
    def invoice_cancel(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        row = 0
        for record in self.env['businesstax.invoice'].browse(active_ids):
            record.update({
                'state': 'open',
                'date_print': '',
                'user_id': '',
            })
