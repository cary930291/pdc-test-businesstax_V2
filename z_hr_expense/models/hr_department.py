# -*- coding: utf-8 -*-
# Author:EricTang.

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    x_studio_dept_category = fields.Selection([
        ('manufacture', '製造'),
        ('sale', '銷售'),
        ('management', '管理'),
        ('research ', '研發'),
    ], string='Dept Category', index=True,   copy=False,
         track_visibility='always')