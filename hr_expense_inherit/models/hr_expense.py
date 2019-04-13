# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.base.models.res_users import parse_m2m
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from odoo.tools import float_compare


class HrExpense(models.Model):
    _inherit = 'hr.expense'
    _order = 'create_date desc'
    name = fields.Char('Description', readonly=True, required=True,
                       states={'draft': [('readonly', False)], 'approve': [('readonly', False)],
                               'cancel': [('readonly', False)]})
    date = fields.Date(readonly=True, states={'draft': [('readonly', False)], 'approve': [('readonly', False)],
                                              'post': [('readonly', True)]}, default=fields.Date.context_today,
                       string="Date")

    quantity = fields.Float(required=True, readonly=True,
                            states={'draft': [('readonly', False)], 'approve': [('readonly', False)],
                                    'post': [('readonly', True)]}, digits=dp.get_precision('Product Unit of Measure'),
                            default=1)
    product_id = fields.Many2one('product.product', string='Product', readonly=True,
                                 states={'draft': [('readonly', False)], 'approve': [('readonly', False)],
                                         'cancel': [('readonly', False)]}, domain=[('can_be_expensed', '=', True)],
                                 required=True)
    unit_amount = fields.Float("Unit Price", readonly=True, required=True,
                               states={'draft': [('readonly', False)], 'approve': [('readonly', False)],
                                       'cancel': [('readonly', False)]},
                               digits=dp.get_precision('Product Price'), )

    tax_ids = fields.Many2many('account.tax', 'expense_tax', 'expense_id', 'tax_id', string='Taxes',
                               readonly=True,
                               states={'draft': [('readonly', False)], 'approve': [('readonly', False)],
                                       'cancel': [('readonly', False)]}, )

    def _update_line_info(self, values):
        orders = self.mapped('sheet_id')
        for order in orders:
            msg = "<b>费用报告如下更新：</b><ul>"
            for line in order.expense_line_ids:
                precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                if 'quantity' in values and float_compare(line.quantity, values['quantity'],
                                                          precision_digits=precision) != 0:
                    msg += "<li> %s:" % (line.product_id.display_name,)
                    msg += "<br/>" + "数量" + ": %s -> %s <br/>" % (
                        line.quantity, float(values['quantity']),)
                if 'unit_amount' in values and float_compare(line.unit_amount, values['unit_amount'],
                                                             precision_digits=precision) != 0:
                    msg += "<li> %s:" % (line.product_id.display_name,)
                    msg += "<br/>" + "单价" + ": %s -> %s <br/>" % (
                        line.unit_amount, float(values['unit_amount']),)

                if 'tax_ids' in values:
                    tax_id = set(parse_m2m(values.get('tax_ids') or []))
                    new_tax = self.env['account.tax'].browse(tax_id)
                    print(list(tax_id))
                    print(line.tax_id.ids)
                    if list(tax_id) != line.tax_ids.ids:
                        msg += "<li> %s:" % (line.product_id.display_name,)
                        msg += "<br/>" + "税率" + ": %s -> %s <br/>" % (
                            line.tax_ids.name if line.tax_ids else '未税', new_tax.name,)

            msg += "</ul>"
            order.message_post(body=msg)

    @api.multi
    def write(self, values):
        for r in self:
            if r.sheet_id.state == 'approve' and (
                    (not r.user_has_groups('account.group_account_user')) and (not r.user_has_groups(
                'account.group_account_manager')) and (not self.user_has_groups('account.group_account_invoice'))) \
                    and ('quantity' in values or 'unit_amount' in values or 'tax_ids' in values or 'product_id' in values):
                raise UserError('只有财务人员可以修改审核完成的单据')

            if 'quantity' in values or 'unit_amount' in values or 'tax_ids' in values or 'product_id' in values:
                precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                self.filtered(
                    lambda r: r.state not in ('cancel', 'draft'))._update_line_info(values)

        return super(HrExpense, self).write(values)

    payment_mode = fields.Selection([
        ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company")
    ], default='own_account',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)], 'approve': [('readonly', False)],
                'cancel': [('readonly', False)]},
        string="Paid By")

    state = fields.Selection([
        ('draft', u'草稿'),
        ('cancel', u'被拒'),
        ('reviewing', u'待批准'),
        ('approve', u'已批准'),
        ('post', u'已过账'),
        ('done', u'已支付'),
    ], compute='_compute_state', string='Status', copy=False, index=True, readonly=True, store=True,
        help="Status of the expense.")

    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id or expense.sheet_id.state == 'draft':
                expense.state = "draft"
            elif expense.sheet_id.state == "cancel":
                expense.state = "cancel"
            elif expense.sheet_id.state == "reviewing":
                expense.state = "reviewing"
            elif expense.sheet_id.state == "approve" or expense.sheet_id.state == "post":
                expense.state = "approve"
            elif not expense.sheet_id.account_move_id:
                expense.state = "reported"
            else:
                expense.state = "done"
