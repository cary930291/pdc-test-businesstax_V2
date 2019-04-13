# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrExpenseSheet(models.Model):
    _inherit = "account.payment"

    destination_account_id = fields.Many2one('account.account',
                                             compute='_compute_destination_account_id', readonly=False)
