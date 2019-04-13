# -*- coding: utf-8 -*-
# Author:EricTang.

from odoo import fields, models

class HrExpenseMapping(models.Model):
    _name = 'hr.expense.mapping'

    product_id = fields.Many2one('product.product', string='Product',
                                 domain=[('can_be_expensed', '=', True)], required=True)
    expense_account_id = fields.Many2one('account.account', string='Expense Account', help="An expense account is expected")
    manufacture_account_id = fields.Many2one('account.account', string='Manufacture Account', help="An manufacture account is expected")
    sale_account_id = fields.Many2one('account.account', string='Sale Account', help="An sale account is expected")
    management_account_id = fields.Many2one('account.account', string='Management Account', help="An management account is expected")
    research_account_id = fields.Many2one('account.account', string='Research Account', help="An research account is expected")

