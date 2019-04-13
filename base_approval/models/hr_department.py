# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    auth_id = fields.Many2one('hr.department.auth.settings', string=u'相关权限')


class HrAuthSettings(models.Model):
    _name = 'hr.department.auth.settings'
    name = fields.Char(string='名称')

    expense_amount = fields.Float(string=u'费用金额')
    info_user_ids = fields.Many2many('res.users', string=u'通知人员')
    line_ids = fields.One2many('hr.department.auth.settings.line', 'setting_id')


class HrAuthSettingsLine(models.Model):
    _name = 'hr.department.auth.settings.line'
    _order = 'sequence'
    setting_id = fields.Many2one('hr.department.auth.settings')
    sequence = fields.Integer(default=10)
    user_id = fields.Many2one('res.users', string=u'人员')
    advanced = fields.Boolean(string=u'加签', help='主管签核完成之后再签核', default=True)
    remark = fields.Char(string=u'备注')
