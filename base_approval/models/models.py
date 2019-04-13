# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare


class ApproveRecords(models.Model):
    _name = "approval.records"

    """
    按照部门架构审核的审核记录表
    """
    _order = 'id desc'

    res_id = fields.Integer(string=u"关联model数据库id")

    res_model = fields.Char(string=u"关联model名")

    user_id = fields.Many2one('res.users', string=u"审核人")

    status = fields.Selection([
        ('0', '通过'),
        ('1', '拒绝'),
        ('2', '提交'),
        ('3', '撤回'),
    ], string=u"审核状态")

    remark = fields.Char(string=u"备注")


class BaseApprove(models.AbstractModel):
    _name = "base.approval"

    state = fields.Selection([
        ('draft', u'草稿'),
        ('cancel', u'被拒'),
        ('reviewing', u'待审核'),
        ('rejected', u'拒绝'),
        ('done', u'完成'),
    ], string=u"状态", default='draft', track_visibility='onchange')

    to_approval_department_id = fields.Many2one('hr.department', string=u"待审核部门")

    # to_approval_employee_id = fields.Many2one('hr.employee', string=u"待审核人",
    #                                           related='to_approval_department_id.manager_id')

    to_approve_user_id = fields.Many2one('res.users')

    user_can_approve = fields.Boolean(compute='compute_user_can_approve')
    user_can_submit = fields.Boolean(compute='compute_user_can_submit')
    user_can_retract = fields.Boolean(compute="_compute_user_can_retract")
    user_id = fields.Many2one('res.users', help='提交人即为该单据的负责人', compute='get_user_id', store=True)
    approve_id = fields.Many2one('res.users', string=u'审核人')
    approval_record_ids = fields.One2many('approval.records', 'res_id')

    @api.multi
    def get_user_id(self):
        for r in self:
            r.user_id = r.create_uid.id

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        args = domain or []
        if self._context.get('approve_type') == 'submitted' and self.env.user.employee_ids:
            approvals = self.env['approval.records'].search([
                ('res_model', '=', self._name),
                ('status', '=', '2'),
                ('user_id', '=', self.env.user.employee_ids[0].id)
            ])
            res_ids = approvals.mapped('res_id')
            domain = [('id', 'in', res_ids), ('state', 'not in', ('draft', 'rejected'))]
            args = domain + args
        elif self._context.get('approve_type') == 'approved' and self.env.user.employee_ids:

            approvals = self.env['approval.records'].search([
                ('res_model', '=', self._name),
                ('status', 'in', ['0', '1']),
                ('user_id', '=', self.env.user.employee_ids[0].id)
            ])
            res_ids = approvals.mapped('res_id')
            domain = [('id', 'in', res_ids)]
            args = domain + args
        return super(BaseApprove, self).search_read(domain=args, fields=fields, offset=offset, limit=limit,
                                                    order=order)

    def create_approve_record(self, remark='', status=False):
        self.env['approval.records'].create({
            'res_id': self.id,
            'res_model': self._name,
            'remark': remark,
            'user_id': self.env.user.id,
            'status': status
        })

    @api.model
    def _needaction_domain_get(self):
        """ Returns the domain to filter records that require an action
            :return: domain or False is no action
        """

        if self._context.get('approve_type') == 'to_submit':
            return [('state', 'in', ('draft', 'rejected')), ('create_uid', '=', self.env.user.id)]
        if self._context.get('approve_type') == 'to_approve':
            return [('to_approval_employee_id.user_id', '=', self.env.user.id)]

    @api.multi
    def compute_user_can_submit(self):
        for r in self:
            if r.create_uid == self.env.user:
                r.user_can_submit = True
            else:
                r.user_can_submit = False

    @api.multi
    def _compute_user_can_retract(self):
        for record in self:

            if record.user_id.id == self.env.uid and record.state == 'reviewing':
                record.user_can_retract = True
            else:
                record.user_can_retract = False

    def compute_user_can_approve(self):
        if not self.env.user.employee_ids:
            self.user_can_approve = False
        if self.to_approve_user_id and self.to_approve_user_id.id == self.env.user.id:
            self.user_can_approve = True
        else:
            self.user_can_approve = False

    def get_approve_department_id(self):
        return self.department_id

    @api.multi
    def action_comment(self):
        """
        审核动作
        :return:
        """
        return {
            'type': 'ir.actions.act_window',
            'name': u'审核意见',
            'res_model': 'to.approval.action.wizard',
            'view_mode': 'form',
            'context': {'default_res_id': self.id, 'default_res_model': self._name},
            'view_id': self.env.ref('base_approval.approval_comment_wizard_form').id,
            'target': 'new'
        }

    @api.multi
    def action_account_reject(self):
        """
        审核动作
        :return:
        """
        return {
            'type': 'ir.actions.act_window',
            'name': u'审核意见',
            'res_model': 'to.approval.action.wizard',
            'view_mode': 'form',
            'context': {'default_res_id': self.id, 'default_res_model': self._name},
            'view_id': self.env.ref('base_approval.approval_account_reject_wizard_form').id,
            'target': 'new'
        }

    @api.multi
    def action_retract(self):
        """
        撤回的动作
        :return:
        """
        return {
            'type': 'ir.actions.act_window',
            'name': u'撤回',
            'res_model': 'to.approval.action.wizard',
            'view_mode': 'form',
            'context': {'default_res_id': self.id, 'default_res_model': self._name},
            'view_id': self.env.ref('base_approval.approval_retract_wizard_form').id,
            'target': 'new'
        }

    def check_values(self):
        """
        用于检查是否可以提交
        :return:
        """

    def send_info_mail(self, users):
        if users:
            # admin_id = self.env.ref('base.user_admin')
            mail = self.env['mail.compose.message'].sudo(7).with_context(active_model='hr.expense.sheet',
                                                                         active_id=self.id).create(
                {
                    'body': self.name,
                    'author_id': self.create_uid.partner_id.id,
                    'partner_ids': [(4, user.partner_id.id) for user in users],
                    'subject': self.user_id.name + self.name + '费用报销通知',
                    'mail_server_id': self.env['ir.mail_server'].sudo().search([])[0].id,
                    'auto_delete_message': True,
                    'auto_delete': True,

                })
            try:
                print(mail.partner_ids)

                mail.send_mail()
            except:

                pass

    def _set_approve_user_id(self, user_id):
        if not user_id:
            raise UserError(u'找不到审核人')
        if not user_id.partner_id:
            raise UserError('找不到审核人对应的partner')
        self.to_approve_user_id = user_id.id
        if not self.create_uid.partner_id:
            raise UserError(u'找不到创建人对应的partner')

        # admin_id=self.env.ref('base.user_admin')
        # print (admin_id)
        mail = self.env['mail.compose.message'].sudo(7).with_context(active_model='hr.expense.sheet',
                                                                     active_id=self.id).create(
            {
                'body': self.name,
                'author_id': self.create_uid.partner_id.id,
                'partner_ids': [(4, user_id.partner_id.id)],
                'model': 'hr.expense.sheet',
                'subject': self.user_id.name + ' ' + self.name + u'费用待审核',
                'mail_server_id': self.env['ir.mail_server'].sudo().search([])[0].id,

            })
        try:

            mail.send_mail()
        except:

            pass

    # 提交审核
    def action_submit(self, need_notification=False):
        # 提交人即为该单据负责人，退回的时候可以退给他
        # 创建审核记录
        self.check_values()
        self.create_approve_record(status='2')

        department_id = self.get_approve_department_id()
        # 如果部门没有配置权限或者没有配置签核人
        if department_id and not department_id.auth_id:
            raise UserError(u'部门没有配置审核权限')
        line_ids = department_id.auth_id.line_ids.filtered(lambda x: x.advanced == True)
        if department_id and not line_ids:
            to_approve_id = department_id.manager_id.user_id
            # self._set_approve_user_id(department_id.manager_id.user_id)
        else:
            to_approve_id = line_ids[0].user_id
            # self._set_approve_user_id(line_ids[0].user_id)
        self.with_context(tracking_disable=True)._set_approve_user_id(to_approve_id)
        self.to_approval_department_id = department_id.id
        if department_id and department_id.auth_id and department_id.auth_id.info_user_ids:
            self.with_context(tracking_disable=True).send_info_mail(department_id.auth_id.info_user_ids)
        self.state = "reviewing"

        # if need_notification:
        #     self.send_notification_oa(('%s %s' % (self._description, self.name)), '等待审核',self.sudo().rt_to_approval_department_id.manager_id.user_id.id)

    # 撤回
    def action_cancel_approval(self, remark=False):
        if remark:
            reject_str = "撤回原因：" + remark
            self.message_post(body=reject_str)
        self.create_approve_record(status='3', remark=remark)
        self.state = "draft"
        self.to_approval_department_id = False
        self.to_approve_user_id = False

    def set_to_reject(self):
        self.state = 'rejected'

    def action_reject(self, remark='', need_notification=False):
        if remark:
            reject_str = "拒绝原因：" + remark
            self.message_post(body=reject_str)
        # admin_id = self.env['res.users']
        self.sudo(7).message_post_with_view('hr_expense.hr_expense_template_refuse_reason',
                                            values={'reason': remark, 'is_sheet': True, 'name': self.name})
        self.create_approve_record(status='1', remark=remark)
        self.set_to_reject()
        self.to_approval_department_id = False
        self.to_approve_user_id = False

    # 审核通过
    def action_approve(self, remark=''):
        self.create_approve_record(status='0', remark=remark)
        reject_str = "审核通过：" + remark
        self.message_post(body=reject_str)
        if self.to_approval_department_id.manager_id.user_id == self.env.user:
            if self.to_approval_department_id.parent_id.id:
                parent_department_id = self.to_approval_department_id.parent_id
                self.to_approval_department_id = parent_department_id.id
                if parent_department_id.auth_id and parent_department_id.auth_id.info_user_ids:
                    self.send_info_mail(parent_department_id.auth_id.info_user_ids)
                    self.to_approve_user_id = self.parent_department_id.manager_id.user_id.id
                if parent_department_id.auth_id.line_ids:
                    self.to_approve_user_id = parent_department_id.auth_id.line_ids[0].user_id.id
                self.to_approve_user_id = self.to_approval_department_id.parent_id.manager_id.user_id
            else:
                self.action_approve_done()
        else:
            line_ids = self.to_approval_department_id.auth_id.line_ids
            line_id = line_ids.filterd(lambda x: x.user_id == self.env.user)
            index = line_ids.indexof(line_id)
            if index < len(line_ids) - 1:
                self.to_approve_user_id = line_ids[index + 1].user_id
            else:
                self.to_approve_user_id = self.to_approval_department_id.manager_id.user_id

    def set_to_done(self):
        self.state = 'approve'

    def action_approve_done(self, need_notification=False):

        self.to_approval_department_id = False
        self.approve_id = self.env.user.id
        self.to_approve_user_id = False
        self.set_to_done()

    @api.multi
    def unlink(self):
        for r in self:
            if r.state not in ('draft', 'cancel'):
                raise UserError('只可删除草稿状态的单据')
        return super(BaseApprove, self).unlink()


class ApprovalActionWizard(models.TransientModel):
    """
        没有审核流的审核动作
    """
    _name = "to.approval.action.wizard"

    res_model = fields.Char()
    remark = fields.Text(string=u'备注')

    def submit(self):
        context = dict(self._context or {})

        active_ids = context.get('active_ids', [])
        model_ids = self.env[self.res_model].browse(active_ids)
        model_ids.action_submit()

    def reject(self):
        if not self.remark:
            raise UserError(u'审核意见必填')
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        model_ids = self.env[self.res_model].browse(active_ids)
        remark = self.remark if self.remark else ''
        model_ids.action_reject(remark=remark)

    def approve(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        model_ids = self.env[self.res_model].browse(active_ids)
        remark = self.remark if self.remark else ''
        model_ids.action_approve(remark=remark)

    def retract(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        model_ids = self.env[self.res_model].browse(active_ids)
        remark = self.remark if self.remark else ''
        model_ids.action_cancel_approval(remark=remark)
