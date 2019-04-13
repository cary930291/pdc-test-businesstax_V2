# -*- coding: utf-8 -*-
import json

from odoo import models, fields, api, _
from odoo.addons.base.models.res_users import parse_m2m
from odoo.exceptions import UserError, ValidationError
from odoo.tests import ADMIN_USER_ID

from odoo.tools import float_is_zero, float_compare

import datetime


class HrExpenseSheet(models.Model):
    _name = 'hr.expense.sheet'
    _inherit = ['base.approval', 'hr.expense.sheet']

    user_can_modify = fields.Boolean(compute='compute_can_modify')

    name = fields.Char('Description', readonly=True, required=True,
                       states={'draft': [('readonly', False)], 'approve': [('readonly', False)],
                               'cancel': [('readonly', False)]})

    @api.multi
    def refuse_sheet(self, reason):
        if not self.user_has_groups('hr_expense.group_hr_expense_user'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot refuse your own expenses"))

            if not self.env.user in current_managers:
                raise UserError(_("You can only refuse your department expenses"))

        self.write({'state': 'cancel'})
        for sheet in self:
            # admin_id=self.env.ref('base.user_admin')
            sheet.sudo(7).message_post_with_view('hr_expense.hr_expense_template_refuse_reason',
                                                 values={'reason': reason, 'is_sheet': True, 'name': self.name})
        self.activity_update()

    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids, template):
        """ Notify new followers, using a template to render the content of the
        notification message. Notifications pushed are done using the standard
        notification mechanism in mail.thread. It is either inbox either email
        depending on the partner state: no user (email, customer), share user
        (email, customer) or classic user (notification_type)

        :param partner_ids: IDs of partner to notify;
        :param template: XML ID of template used for the notification;


        """
        print ('111111111111111111111')
        return

    @api.multi
    def compute_can_modify(self):
        for r in self:
            if r.state == 'approve' and (self.user_has_groups('account.group_account_user') or self.user_has_groups(
                    'account.group_account_manager') or self.user_has_groups('account.group_account_invoice')):
                r.user_can_modify = True
            else:
                r.user_can_modify = False

    state = fields.Selection([
        ('draft', u'草稿'),
        ('reviewing', u'待批准'),
        ('cancel', u'被拒'),
        ('approve', u'已批准'),
        ('post', u'已过账'),
        ('done', u'已支付'),
    ], string=u"状态", default='draft', track_visibility='onchange')
    approval_record_ids = fields.One2many('approval.records', 'res_id',
                                          domain=[('res_model', '=', 'hr.expense.sheet')])

    expense_line_ids = fields.One2many('hr.expense', 'sheet_id', string='Expense Lines',
                                       states={'approve': [('readonly', True)], 'done': [('readonly', True)],
                                               'draft': [('readonly', False)],
                                               'post': [('readonly', True)]}, copy=False)

    def set_to_reject(self):
        self.state = 'cancel'
        self.is_refused = True
        print('dddd')

    @api.model
    def _needaction_domain_get(self):
        """ Returns the domain to filter records that require an action
            :return: domain or False is no action
        """
        print(self._context)
        if self._context.get('approve_type') == 'to_submit':
            return [('state', 'in', ('draft', 'rejected')), ('create_uid', '=', self.env.user.id)]
        if self._context.get('approve_type') == 'to_approve':
            return [('to_approval_employee_id.user_id', '=', self.env.user.id)]

    # 审核通过
    def action_approve(self, remark=''):
        self.create_approve_record(status='0', remark=remark)
        reject_str = "审核通过：" + remark
        self.message_post(body=reject_str)
        to_approve_user_id = False
        after_line_ids = self.to_approval_department_id.auth_id.line_ids.filtered(lambda x: x.advanced == False)

        if self.to_approval_department_id.manager_id.user_id == self.env.user:

            if self.total_amount <= self.to_approval_department_id.get_hr_expense_perm_amount() or (
                    not self.to_approval_department_id.parent_id and not after_line_ids):
                self.action_approve_done()
            elif after_line_ids:
                # self._set_approve_user_id(after_line_ids[0].user_id)
                to_approve_user_id = after_line_ids[0].user_id
            else:
                parent_department_id = self.to_approval_department_id.parent_id
                self.to_approval_department_id = parent_department_id.id
                if parent_department_id.auth_id and parent_department_id.auth_id.line_ids.filtered(
                        lambda x: x.advanced == True):
                    to_approve_user_id = \
                        parent_department_id.auth_id.line_ids.filtered(lambda x: x.advanced == True)[0].user_id
                    # self._set_approve_user_id(to_approve_user_id)
                else:
                    if not parent_department_id.manager_id.user_id:
                        raise UserError('%s没找到对应的部门负责人' % parent_department_id.name)
                    to_approve_user_id = parent_department_id.manager_id.user_id
                    # self._set_approve_user_id(parent_department_id.manager_id.user_id)

        else:
            advance_line_ids = self.to_approval_department_id.auth_id.line_ids.filtered(lambda x: x.advanced == True)
            after_line_ids = self.to_approval_department_id.auth_id.line_ids.filtered(lambda x: x.advanced == False)
            advance_line_id = advance_line_ids.filtered(lambda x: x.user_id == self.env.user)
            after_line_id = after_line_ids.filtered(lambda x: x.user_id == self.env.user)
            if advance_line_id:
                index = list(advance_line_ids).index(advance_line_id)
                if index < len(advance_line_ids) - 1:
                    # self._set_approve_user_id(advance_line_ids[index + 1].user_id)
                    to_approve_user_id = advance_line_ids[index + 1].user_id
                else:
                    # self._set_approve_user_id(self.to_approval_department_id.manager_id.user_id)
                    to_approve_user_id = self.to_approval_department_id.manager_id.user_id
            else:
                index = list(after_line_ids).index(after_line_id)
                if index < len(after_line_ids) - 1:
                    to_approve_user_id = after_line_ids[index + 1].user_id
                    # self._set_approve_user_id(after_line_ids[index + 1].user_id)
                else:
                    if self.total_amount <= self.to_approval_department_id.get_hr_expense_perm_amount() or \
                            not self.to_approval_department_id.parent_id:
                        self.action_approve_done()
                    else:
                        parent_department_id = self.to_approval_department_id.parent_id
                        self.to_approval_department_id = parent_department_id

                        if parent_department_id.auth_id and parent_department_id.auth_id.line_ids.filtered(
                                lambda x: x.advanced == True):
                            to_approve_user_id = \
                                parent_department_id.auth_id.line_ids.filtered(lambda x: x.advanced == True)[
                                    0].user_id
                            # self._set_approve_user_id(to_approve_user_id)
                        else:
                            to_approve_user_id = parent_department_id.manager_id.user_id
                            # self._set_approve_user_id(to_approve_user_id)
        if to_approve_user_id:
            self._set_approve_user_id(to_approve_user_id)

    department_id = fields.Many2one('hr.department', string=u'部门',
                                    track_visibility='onchange',
                                    states={'post': [('readonly', False)], 'done': [('readonly', False)],
                                            'salary': [('readonly', False)]})

    def check_values(self):
        if not self.expense_line_ids:
            raise UserError(u'请添加报销明细')

    @api.multi
    def write(self, values):

        if self.state == 'approve' and (
                (not self.user_has_groups('account.group_account_user')) and (not self.user_has_groups(
            'account.group_account_manager')) and (not self.user_has_groups('account.group_account_invoice'))) \
                and 'expense_line_ids' in values:
            raise UserError('只有财务人员可以修改审核完成的单据')

        return super(HrExpenseSheet, self).write(values)

#
#
#
# class HrExpenseRefuseWizard(models.TransientModel):
#     _inherit = "hr.expense.refuse.wizard"
#
#     @api.multi
#     def expense_refuse_reason(self):
#         self.ensure_one()
#
#         context = dict(self._context or {})
#         active_ids = context.get('active_ids', [])
#         expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
#         expense_sheet.refuse_expenses(self.description)
#         return {'type': 'ir.actions.act_window_close'}
