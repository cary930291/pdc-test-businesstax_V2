# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero

from odoo.addons import decimal_precision as dp


class BusinessTaxYear(models.Model):
    _name = 'businesstax.year'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Year Master Data"

    name =  fields.Char(string='Name', index=True, required=True,translate =True, track_visibility='always')

class BusinessTaxPeriod(models.Model):
    _name = 'businesstax.period'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Period Master Data"

    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

class BusinessTaxProfixType(models.Model):
    _name = 'businesstax.profix.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Profix Type Master Data"

    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

class BusinessTaxProfixType(models.Model):
    _name = 'businesstax.certificate.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Certificate.Category Master Data"
    code =  fields.Char(string='Code', index=True, required=True, track_visibility='always')
    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

    def name_get(self):
        result = []
        for group in self:
            if group.code:
                name = group.code + ' ' + group.name
            result.append((group.id, name))
        return result

class BusinessTaxStatus(models.Model):
    _name = 'businesstax.status'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Status Master Data"

    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

class BusinessTaxVatDeclareCode(models.Model):
    _name = 'businesstax.vat.declare.code'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Vat Declare Code Master Data"
    code =  fields.Char(string='Code', index=True, required=True, track_visibility='always')
    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

    def name_get(self):
        result = []
        for group in self:
            if group.code:
                name = group.code + ' ' + group.name
            result.append((group.id, name))
        return result

class BusinessTaxType(models.Model):
    _name = 'businesstax.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Type Master Data"
    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

class BusinessTaxTaxCodeType(models.Model):
    _name = 'businesstax.tax.code.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Tax Code Type Master Data"
    code =  fields.Char(string='Code', index=True, required=True, track_visibility='always')
    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

    def name_get(self):
        result = []
        for group in self:
            if group.code:
                name = group.code + ' ' + group.name
            result.append((group.id, name))
        return result

class BusinessTaxDeclareDeduction(models.Model):
    _name = 'businesstax.declare.deduction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Declare Deduction Master Data"
    code =  fields.Char(string='Code', index=True, required=True, track_visibility='always')
    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

    def name_get(self):
        result = []
        for group in self:
            if group.code:
                name = group.code + ' ' + group.name
            result.append((group.id, name))
        return result

class BusinessTaxThroughCustom(models.Model):
    _name = 'businesstax.through.custom'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Through Custom Master Data"
    code =  fields.Char(string='Code', index=True, required=True, track_visibility='always')
    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

    def name_get(self):
        result = []
        for group in self:
            if group.code:
                name = group.code + ' ' + group.name
            result.append((group.id, name))
        return result

class BusinessTaxDeclareType(models.Model):
    _name = 'businesstax.declare.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Declare Type Master Data"
    code =  fields.Char(string='Code', index=True, required=True, track_visibility='always')
    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

    def name_get(self):
        result = []
        for group in self:
            if group.code:
                name = group.code + ' ' + group.name
            result.append((group.id, name))
        return result

class BusinessTaxHDType(models.Model):
    _name = 'businesstax.hd.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config HD Type Master Data"
    code =  fields.Char(string='Code', index=True, required=True, track_visibility='always')
    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')

    def name_get(self):
        result = []
        for group in self:
            if group.code:
                name = group.code + ' ' + group.name
            result.append((group.id, name))
        return result

class BusinessTaxVatDeclareMapping(models.Model):
    _name = 'businesstax.vat.declare.mapping'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Config Vat Declare Mapping Master Data"
    type = fields.Many2one('businesstax.type', string='Type', store=True, track_visibility='always')
    certificate_category = fields.Many2one('businesstax.certificate.category', string='Certificate Category',
                                           store=True, track_visibility='always')
    vat_declare_code = fields.Many2one('businesstax.vat.declare.code', string='Vat Declare Code', store=True, track_visibility='always')