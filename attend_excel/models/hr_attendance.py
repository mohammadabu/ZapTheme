import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
import logging
from odoo.tools import date_utils
_logger = logging.getLogger(__name__)
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class AttendanceReportExcel(models.TransientModel):
    _name = "wizard.attendance.history.excel"
    _description = "Current Attendance History in Excel"

    from_date = fields.Date()
    to_date = fields.Date()
    employees = fields.Many2many('hr.employee', required=True)
    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'employees': self.employees.ids,
        }
        all_employee_attendance =  self.pool.get("wizard.attendance.history.excel").get_employee_attendance(self)
        
        # return {
        #     'type': 'ir_actions_xlsx_download',
        #     'data': {'model': 'wizard.attendance.history.excel',
        #              'options': json.dumps(data, default=date_utils.json_default),
        #              'output_format': 'xlsx',
        #              'report_name': 'Current Attendance History',
        #             }
        # }
    @api.model
    def get_employee_attendance(self):
        table_excel = {}
        employees = 125
        from_date = '2021-06-01'
        to_date = '2021-06-30'
        _logger.info('--------------------')
        _logger.info(employees)
        _logger.info(from_date)
        _logger.info(to_date)
        employee_info = self.env['hr.employee'].sudo.search([('id', '=', employees)])
        _logger.info(to_date)
        _logger.info('--------------------')
