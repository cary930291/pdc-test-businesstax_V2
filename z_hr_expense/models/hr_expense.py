# -*- coding: utf-8 -*-
# Author:EricTang.

from odoo import fields, models, api


class HrDepartment(models.Model):
    _inherit = 'hr.expense'

    @api.model
    @api.onchange('product_id', 'employee_id')
    def _onchange_product_id(self):
        res = super(HrDepartment, self)._onchange_product_id()
        if self.product_id:
            if not self.name:
                self.name = self.product_id.display_name or ''
            self.unit_amount = self.product_id.price_compute('standard_price')[self.product_id.id]
            self.product_uom_id = self.product_id.uom_id
            self.tax_ids = self.product_id.supplier_taxes_id

            # 增加部門比對會計科目判斷
            # ('manufacture', '製造'),
            # ('sale', '銷售'),
            # ('management', '管理'),
            # ('research ', '研發'),
            _org_name = self.employee_id.department_id.x_studio_dept_category
            _dept_account = self.env['hr.expense.mapping'].search([('product_id','=',self.product_id.id)])

            if _dept_account:
                if _org_name == '管理':
                    account = _dept_account.management_account_id
                elif _org_name == '製造':
                    account = _dept_account.manufacture_account_id
                elif _org_name == '銷售':
                    account = _dept_account.sale_account_id
                elif _org_name == '研發':
                    account = _dept_account.research_account_id
                else:
                    account = _dept_account.expense_account_id
            else:
                account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                self.account_id = account
        return res