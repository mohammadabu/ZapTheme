# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import email_split


class HrLeave(models.Model):
    _inherit = 'hr.leave'