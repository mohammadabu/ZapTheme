from odoo import models, fields, api

class HrEmployeeDocuments(models.Model):
    _inherit = 'hr.employee'

    salary_definition = fields.Char()

    job_definition = fields.Char()