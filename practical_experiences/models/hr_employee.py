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
    from_date = fields.Date()
    to_date = fields.Date()
    attachment = fields.Binary()
    summary = fields.Html()
    employee_id = fields.Many2one('hr.employee',default=lambda self: self.env.context.get('active_id', []))


class CustomHrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_practical_experiences(self):
        count_value = self.env['hr.employee.practical.experiences'].search_count([('employee_id','=',self.id)])
        self.practical_experiences = count_value
    practical_experiences = fields.Integer(string="practical experiences",compute="get_practical_experiences")

    def open_practical_experiences(self):
        return{
            'name':"Practical Experiences",
            'domain':[('employee_id','=',self.id)],
            'type':'form',
            'res_model':'hr.employee.practical.experiences',
            'view_id':False,
            'view_mode':'tree,form',
            'type':'ir.actions.act_window',
            'target':'list'
        }