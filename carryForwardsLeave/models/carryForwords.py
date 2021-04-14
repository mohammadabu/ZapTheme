# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)
import re
from datetime import datetime, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import email_split



class HrLeave(models.Model):
    _inherit = 'hr.leave'    

class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    check_forword = fields.Boolean()


class HrLeaveTypesCarryForwards(models.Model):
    _inherit = 'hr.leave.type'
    carry_forwards_validators = fields.One2many('hr.holidays.carry.forwards',
                                       'hr_holiday_status',
                                       string='Carry Forwards Validators', help="Carry Forwards validators")  

    carry_forwards = fields.Boolean('Carry Foward?')   
    automatically_leave = fields.Boolean('Automatically Leave Creation?')                                 
    time_off_type = fields.Many2one('hr.leave.type',string='Time off Type', help="Time off Type")  
    timeoff_name = fields.Char('Time Off Name')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    finished_carry_froword = fields.Boolean()
    def _get_approval_requests(self):
        current_uid = self.env.uid
        employees = self.env['hr.employee'].sudo().search([('user_id','=',self.env.uid)])
        li = []
        for employee in employees:
            hr_holidays = self.env['hr.leave.allocation'].sudo().search([('employee_id','=',employee.id)])
            for l in hr_holidays:
                li.append(l.id)                              
        value = {
            'domain': str([('id', 'in', li)]),
            'view_mode': 'tree,form',
            'res_model': 'hr.leave.allocation',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Carry Forwards'),
            'res_id': self.id,
            'target': 'current',
            'create': False,
            'edit': False,
        }
        return value 

    def carryForwordsDaily(self):     
        _logger.info("---------------------------")
        current_date = datetime.now().date()
        annual_leave_type = self.env['hr.leave.type'].sudo().search(['&',('carry_forwards','=','True'),('finished_carry_froword','=',False),'&',('validity_stop','<',current_date)])
        for annual in annual_leave_type:
            _logger.info(annual.validity_stop)


class HrCarryForwardsValidators(models.Model):
    _name = 'hr.holidays.carry.forwards'

    hr_holiday_status = fields.Many2one('hr.leave.type')
    validators_type = fields.Selection(
        [
            ('direct_manager','Direct Manager'),
            ('position','Position'),
            ('user','User')
        ]
    )
    holiday_validators_user = fields.Many2one('res.users',
                                         string='Leave Validators', help="Leave validators",
                                         domain="[('share','=',False)]")
    holiday_validators_position = fields.Many2one('hr.job')                                     
    approval = fields.Boolean()
    exception = fields.Boolean()   
    days = fields.Integer()                           