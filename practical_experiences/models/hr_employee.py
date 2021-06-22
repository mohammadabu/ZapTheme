from odoo import api, models, fields, exceptions, _
import logging
import base64
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from xlrd import open_workbook
import tempfile
_logger = logging.getLogger(__name__)

class PracticalExperiences(models.Model):
    _name = "hr.employee.practical.experiences"
    name = fields.Char()
    practical_experiences = fields.Selection(
        [
            ("training_courses","Training courses"),
            ("certificates","Certificates"),
            ("cv","CV"),
            ("experiences","Experiences")
        ]
    )
    form_date = fields.Date()
    to_date = fields.Date()
    attachment = fields.Binary()
    summary = fields.Html()
    employee_id = fields.Many2one('hr.employee',default=lambda self: self.env.context.get('active_id', []))


class CustomHrEmployee(models.Model):
    _inherit = 'hr.employee'
