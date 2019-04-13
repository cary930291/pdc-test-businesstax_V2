# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class BusinessTaxName(models.Model):
    _name = 'businesstax.name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Basic Master Data"

    name =  fields.Char(string='Name', index=True, required=True, track_visibility='always')
    vat_code = fields.Char(string='Vat Code', index=True, required=True, size = 8 , track_visibility='always')
    tax_code = fields.Char(string='Tax Code', index=True, required=True, size =  9, track_visibility='always')
    company = fields.Many2one('res.company', string='Company', store=True , track_visibility='always')
    owner = fields.Char(string='owner', index=True, required=True, track_visibility='always')
    address = fields.Char(string='address', index=True, required=True, track_visibility='always')
    contact_name = fields.Char(string='contact name', index=True, required=True, track_visibility='always')
    contact_tel = fields.Char(string='contact tel', index=True, required=True, track_visibility='always')
    hd_type = fields.Many2one('businesstax.hd.type',string='hd type', index=True, required=True, track_visibility='always')
    declare_type = fields.Many2one('businesstax.declare.type',string='declare type', index=True, required=True, track_visibility='always')
    direct_deduction = fields.Boolean(string='direct deduction', index=True, required=True, track_visibility='always')
    hd_vat_code = fields.Char(string='hd vat code', index=True, required=True, size =8, track_visibility='always')
    declare_merge = fields.Boolean(string='declare merge', index=True, required=True, track_visibility='always')

class BusinessTaxMethod(models.Model):
    _name = 'businesstax.method'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Area Code Master Data"

    name = fields.Char(string='Name', index=True, required=True, track_visibility='always')
    vat_name = fields.Many2one('businesstax.name', string='Company', store=True , track_visibility='always')
    vat_code = fields.Char(string='Vat Code', index=True, required=True, size = 8 , track_visibility='always')
    auto_invoice = fields.Boolean(string='Auto Invoice', index=True, required=True, track_visibility='always')
    employee = fields.Many2one('hr.employee', string='Employee', store=True , track_visibility='always')
    warehouse = fields.Many2one('stock.warehouse', string='Warehouse', store=True , track_visibility='always')
    location = fields.Many2one('stock.location', string='Location', store=True, track_visibility='always' )
    partner = fields.Many2one('res.partner', string='Partner', store=True, track_visibility='always')
    crm_team = fields.Many2one('stock.location', string='CRM Team', store=True, track_visibility='always')

class BusinessTaxProfix(models.Model):
    _name = 'businesstax.profix'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Profix Master Data"

    name = fields.Char(string='Name', index=True, required=True, track_visibility='always')
    profix_type =  fields.Many2one('businesstax.profix.type', string='Profix Type', index=True, required=True , track_visibility='always')
    year = fields.Many2one('businesstax.year',string='Year', index=True, required=True, track_visibility='always')
    period_start = fields.Many2one('businesstax.period',string='Period Start', index=True, required=True, track_visibility='always')
    period_end = fields.Many2one('businesstax.period',string='Period End', index=True, required=True, track_visibility='always')