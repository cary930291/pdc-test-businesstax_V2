# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = 'hr.department'

    # 该部门允许的采购权限
    def get_hr_expense_perm_amount(self):
        hr_expense_amount = 0
        if self.auth_id:
            hr_expense_amount = self.auth_id.expense_amount
        return hr_expense_amount

    # def get_advance_payment_perm_amount(self):
    #     hr_payment_amount = 0
    #     if self.rt_sign_off_permission_id:
    #         hr_payment_amount = self.rt_sign_off_permission_id.rt_advance
    #     return hr_payment_amount

