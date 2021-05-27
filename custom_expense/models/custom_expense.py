# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)
import re
from datetime import datetime, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import email_split

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