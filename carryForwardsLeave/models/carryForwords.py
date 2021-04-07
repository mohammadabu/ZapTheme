# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import email_split


class HrLeave(models.Model):
    _inherit = 'hr.leave'


class HrLeaveTypesCarryForwards(models.Model):
    _inherit = 'hr.leave.type'
    carry_forwards_validators = fields.One2many('hr.holidays.carry.forwards',
                                       'hr_holiday_status',
                                       string='Carry Forwards Validators', help="Carry Forwards validators")  

    carry_forwards = fields.Boolean('Carry Foward?')                                   



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
    days = fields.Char()                           