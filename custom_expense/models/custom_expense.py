# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)
import re
from datetime import datetime, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import email_split
import logging
_logger = logging.getLogger(__name__)

class CustomExpense(models.Model):
    _inherit = 'hr.expense'
    # state = fields.Selection(selection_add=[('direct', 'Direct Manager')])
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('reported', 'Submitted'),
        ('direct','Direct Manager'),
        ('manager_of_manager','Manager of Manager'),
        ('hr','Hr Manager'),
        ('approved', 'Approved'),
        ('done', 'Paid'),
        ('refused', 'Refused')
    ], compute='_compute_state', string='Status', copy=False, index=True, readonly=True, store=True, help="Status of the expense.")



class HrExpenseSheet(models.Model):

    _inherit = 'hr.expense.sheet'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('direct','Direct Manager'),
        ('manager_of_manager','Manager of Manager'),
        ('hr','Hr Manager'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Refused')
    ], string='Status', index=True, readonly=True, tracking=True, copy=False, default='draft', required=True, help='Expense Report State') 


    @api.model
    def getAllHrManager(self):
        emp_positions = self.env['hr.job'].sudo().search([('internal_id','in',['HR Manager','HR and Administration Manager','HR Officer'])])
        for pos in emp_positions: 
            all_employee = self.env['hr.employee'].sudo().search([('multi_job_id','in',pos.id)])
            for employee in all_employee:
                if employee.user_id != False:
                    _logger.info("------------getAllHrManager-------------")
                    _logger.info(employee.user_id.id)
        # all_employee = self.env['hr.employee'].sudo().search([('multi_job_id','in',default_position.id)])
        # for employee in all_employee:
        #         if employee.user_id != False:
        #             user_email = self.env['res.users'].sudo().search([('id','in',[7,92])])
        all_users = self.env['res.users'].sudo().search([('id','in',[7,92])])  
        self.hr_manager = all_users
    hr_manager = fields.Many2many('res.users','hr_manager',compute='getAllHrManager')


    def approve_expense_direct(self):
        # if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
        #     raise UserError(_("Only Managers and HR Officers can approve expenses"))
        # elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
        #     current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

        #     if self.employee_id.user_id == self.env.user:
        #         raise UserError(_("You cannot approve your own expenses"))

        #     if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
        #         raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'direct', 'user_id': responsible_id})
        self.activity_update()

    def approve_expense_manager_of_manager(self):
        # if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
        #     raise UserError(_("Only Managers and HR Officers can approve expenses"))
        # elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
        #     current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

        #     if self.employee_id.user_id == self.env.user:
        #         raise UserError(_("You cannot approve your own expenses"))

        #     if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
        #         raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'manager_of_manager', 'user_id': responsible_id})
        self.activity_update()  

    def approve_expense_hr(self):
        # if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
        #     raise UserError(_("Only Managers and HR Officers can approve expenses"))
        # elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
        #     current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

        #     if self.employee_id.user_id == self.env.user:
        #         raise UserError(_("You cannot approve your own expenses"))

        #     if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
        #         raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'approve', 'user_id': responsible_id})
        self.activity_update()        