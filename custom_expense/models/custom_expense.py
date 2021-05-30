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
    exp_type = fields.Selection([
        ('operational', 'Operational Orders'),
        ('general', 'General Expenses Orders'),
    ],string="Type")
    reference = fields.Many2one('sale.order')
    
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

    def _get_approval_requests(self):
        """ Action for Approvals menu item to show approval
        requests assigned to current user """
        # _logger.info(employee.user_id.id)       
        hr_expense = self.env['hr.expense.sheet'].sudo().search([('state','in',['submit','direct','manager_of_manager'])])
        li = []
        for l in hr_expense:
            if l.employee_id.parent_id != False:
                if l.employee_id.parent_id.user_id != False:
                    if l.employee_id.parent_id.user_id.id == self.env.user.id: 
                        li.append(l.id)
                    

            if l.employee_id.parent_id.parent_id != False:
                if l.employee_id.parent_id.parent_id.user_id != False:
                    if l.employee_id.parent_id.parent_id.user_id.id == self.env.user.id:
                        li.append(l.id)


            emp_positions = self.env['hr.job'].sudo().search([('internal_id','in',['HR Manager','HR and Administration Manager','HR Officer'])])
            for pos in emp_positions: 
                all_employee = self.env['hr.employee'].sudo().search([('multi_job_id','in',pos.id)])
                for employee in all_employee:
                    if employee.user_id != False:
                        if employee.user_id.id == self.env.user.id:
                            li.append(l.id)
        value = {
            'domain': str([('id', 'in', li)]),
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.sheet',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Approvals'),
            'res_id': self.id,
            'target': 'current',
            'create': False,
            'edit': False,
        }
        return value
        


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


    # @api.model
    # def getAllHrManager(self):
    #     user_list = []
    #     emp_positions = self.env['hr.job'].sudo().search([('internal_id','in',['HR Manager','HR and Administration Manager','HR Officer'])])
    #     for pos in emp_positions: 
    #         all_employee = self.env['hr.employee'].sudo().search([('multi_job_id','in',pos.id)])
    #         for employee in all_employee:
    #             if employee.user_id != False:
    #                 _logger.info("------------getAllHrManager-------------")
    #                 _logger.info(employee.user_id.id)
    #                 user_list.append(employee.user_id.id)


    #     _logger.info("------------all user hr-------------")
    #     _logger.info(user_list)

    #     # all_employee = self.env['hr.employee'].sudo().search([('multi_job_id','in',default_position.id)])
    #     # for employee in all_employee:
    #     #         if employee.user_id != False:
    #     #             user_email = self.env['res.users'].sudo().search([('id','in',[7,92])])
    #     # all_users = self.env['res.users'].sudo().search([('id','in',[7,92])])  
    #     # self.hr_manager = all_users
    #     self.hr_manager = user_list
    # hr_manager = fields.Many2many('res.users','hr_manager',compute='getAllHrManager')
    # hr_manager = fields.Many2many('res.users','hr_manager')



    def approve_expense_direct(self):
        accept = 1
        if self.employee_id.parent_id != False:
            if self.employee_id.parent_id.user_id != False:
                if self.employee_id.parent_id.user_id.id != self.env.user.id:
                    accept = 0
            else:
                accept = 0      
        else:
             accept = 0   

        if accept != 1:
            raise UserError("Only Direct Manager can approve expenses")
        responsible_id = self.user_id.id or self.env.user.id
        responsible_email = self.user_id.login or self.env.user.login
        res_id = self.id
        self.write({'state': 'direct', 'user_id': responsible_id})
        message = "The Direct Manager approved to this activity Expense"
        body_html = self.create_body_for_email(message,res_id)
        employee_id = self.employee_id.id
        email_html = self.create_header_footer_for_email(employee_id,body_html)
        value = {
                'subject': 'Manger Of Manager Approval',
                'body_html': email_html,
                'email_to': responsible_email,
                'email_cc': '',
                'auto_delete': False,
                'email_from': 'axs-sa.com',
        }
        mail_id = self.env['mail.mail'].sudo().create(value)
        mail_id.sudo().send()

    def approve_expense_manager_of_manager(self):
        accept = 1
        if self.employee_id.parent_id.parent_id != False:
            if self.employee_id.parent_id.parent_id.user_id != False:
                if self.employee_id.parent_id.parent_id.user_id.id != self.env.user.id:
                    accept = 0
            else:
                accept = 0      
        else:
             accept = 0   

        if accept != 1:
            raise UserError("Only Manager Of Manager can approve expenses")
        responsible_id = self.user_id.id or self.env.user.id
        responsible_email = self.user_id.login or self.env.user.login
        res_id = self.id
        self.write({'state': 'manager_of_manager', 'user_id': responsible_id})
        message = "The Manager Of Manager approved to this activity Expense"
        body_html = self.create_body_for_email(message,res_id)
        employee_id = self.employee_id.id
        email_html = self.create_header_footer_for_email(employee_id,body_html)
        value = {
                'subject': 'Manager Of Manager Approval',
                'body_html': email_html,
                'email_to': responsible_email,
                'email_cc': '',
                'auto_delete': False,
                'email_from': 'axs-sa.com',
        }
        mail_id = self.env['mail.mail'].sudo().create(value)
        mail_id.sudo().send()
 

    def approve_expense_hr(self):

        accept = 0
        emp_positions = self.env['hr.job'].sudo().search([('internal_id','in',['HR Manager','HR and Administration Manager','HR Officer'])])
        for pos in emp_positions: 
            all_employee = self.env['hr.employee'].sudo().search([('multi_job_id','in',pos.id)])
            for employee in all_employee:
                if employee.user_id != False:
                    if employee.user_id.id == self.env.user.id:
                        accept = 1
        if accept != 1:
            raise UserError("Only Hr Manager can approve expenses")

        responsible_email = self.user_id.login or self.env.user.login
        res_id = self.id
        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'approve', 'user_id': responsible_id})
        message = "The Hr Manager approved to this activity Expense"
        body_html = self.create_body_for_email(message,res_id)
        employee_id = self.employee_id.id
        email_html = self.create_header_footer_for_email(employee_id,body_html)
        value = {
                'subject': 'Hr Manager Approval',
                'body_html': email_html,
                'email_to': responsible_email,
                'email_cc': '',
                'auto_delete': False,
                'email_from': 'axs-sa.com',
        }
        mail_id = self.env['mail.mail'].sudo().create(value)
        mail_id.sudo().send()

    def create_body_for_email(self,message,res_id):
        body_html = ''
        body_html +='<tr>'
        body_html +=    '<td align="center" style="min-width: 590px;">'
        body_html +=        '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
        body_html +=            '<tr>'
        body_html +=                '<td valign="top" style="font-size: 13px;">'
        body_html +=                    '<p style="margin: 0px;font-size: 14px;">'
        body_html +=                        message
        body_html +=                    '</p>'
        body_html +=                    '<p style="margin-top: 24px; margin-bottom: 16px;">'
        body_html +=                        ('<a href="/mail/view?model=hr.expense.sheet&amp;res_id=%s" style="background-color:#875A7B; padding: 10px; text-decoration: none; color: #fff; border-radius: 5px;">') % (res_id)
        body_html +=                            'View Expense Report'
        body_html +=                        '</a>'
        body_html +=                    '</p>'
        body_html +=                    'Thanks,<br/>'
        body_html +=                '</td>'
        body_html +=            '</tr>'
        body_html +=            '<tr>'
        body_html +=                '<td style="text-align:center;">'
        body_html +=                    '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
        body_html +=                '</td>'
        body_html +=            '</tr>'
        body_html +=        '</table>'
        body_html +=    '</td>'
        body_html +='</tr>'
        return body_html
    def create_header_footer_for_email(self,employee_id,body_html):
        employee = self.env['hr.employee'].sudo().search([('id','=',employee_id)])
        company_id = employee.company_id.id
        header = ''
        header += '<table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;">'                      
        header +=   '<tr>'
        header +=       '<td align="center">' 
        header +=           '<table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">'
        header +=               '<tbody>'
        header +=                   '<tr>'
        header +=                       '<td align="center" style="min-width: 590px;">'
        header +=                           '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">'
        header +=                               '<tr><td valign="middle">'
        header +=                                   '<span style="font-size: 10px;">Your Expense Report</span><br/>'
        header +=                                   '<span style="font-size: 20px; font-weight: bold;">'
        header +=                                       (self.name)
        header +=                                   '</span>'
        header +=                               '</td><td valign="middle" align="right">'
        header +=                                  ('<img src="/logo.png?company=%s" style="padding: 0px; margin: 0px; height: auto; width: 80px;" alt=""/>') % (str(company_id))
        header +=                               '</td></tr>'
        header +=                               '<tr><td colspan="2" style="text-align:center;">'
        header +=                                   '<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>'
        header +=                               '</td></tr>'
        header +=                           '</table>'
        header +=                       '</td>'
        header +=                   '</tr>'
        header +=                   body_html
        header +=                   '<tr>' 
        header +=                       '<td align="center" style="min-width: 590px;">' 
        header +=                           '<table border="0" cellpadding="0" cellspacing="0" width="622px" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 24px; border-collapse:separate;">'
        header +=                               '<tr><td valign="middle" align="left">'
        header +=                                   str(employee.company_id.name)
        header +=                               '</td></tr>'
        header +=                               '<tr><td valign="middle" align="left" style="opacity: 0.7;">'
        header +=                                   str(employee.company_id.phone)                
        if employee.company_id.email:
            header += ('<a href="mailto:%s" style="text-decoration:none; color: #454748;">%s</a>') % (str(employee.company_id.email),str(employee.company_id.email))
        if employee.company_id.website:
            header += ('<a href="%s" style="text-decoration:none; color: #454748;">') % (str(employee.company_id.website))    
        header +=                               '</td></tr>'
        header +=                           '</table>'
        header +=                       '</td>'
        header +=                   '</tr>'

        header +=               '</tbody>'
        header +=           '</table>'
        header +=       '</td>'
        header +=     '</tr>'
        header +=     '<tr>'
        header +=       '<td align="center" style="min-width: 590px;">'
        header +=           '<table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: #F1F1F1; color: #454748; padding: 8px; border-collapse:separate;">'
        header +=               '<tr><td style="text-align: center; font-size: 13px;">'
        header +=                   "Powered by "+ ('<a target="_blank" href="%s" style="color: #875A7B;">%s</a>') % (str(employee.company_id.website),str(employee.company_id.name)) 
        header +=               '</td></tr>'
        header +=           '</table>'
        header +=       '</td>'
        header +=     '</tr>'
        header +=   '</table>'
        return header
    