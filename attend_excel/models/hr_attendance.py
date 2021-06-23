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
    def get_employee_attendance(self,index = 0):
        table_excel = {}
        employee_id = 125
        from_date = '2021-06-23'
        to_date = '2021-06-30'
        # _logger.info('--------------------')
        _logger.info(employees)
        _logger.info(from_date)
        _logger.info(to_date)
        employee_info = self.env['hr.employee'].sudo().search([('id', '=', employee_id)])
        id_number = employee_info.employee_id
        employee_name = employee_info.employee_id
        resource_calendar_ids = employee_info.resource_calendar_id
        all_employee_attendance =  self.pool.get("wizard.attendance.history.excel").get_absent_days(self,employee_id,from_date,to_date)
        # table_excel[index] = {}
        # table_excel[index]['id_number'] = id_number
        # table_excel[index]['employee_name'] = employee_name
        # table_excel[index]['employee_name'] = employee_name
        # _logger.info(employee_info)
        # _logger.info(employee_info.employee_id)
        # _logger.info(employee_info.resource_calendar_id)
        # for resource_calendar_id in resource_calendar_ids.attendance_ids:
        #     _logger.info(resource_calendar_id.dayofweek)
        #     _logger.info(resource_calendar_id.day_period)
        #     _logger.info(resource_calendar_id.hour_from)
        #     _logger.info(resource_calendar_id.hour_to)
        # _logger.info('--------------------')

    @api.model
    def get_absent_days(self,employee_id,from_date,to_date):
        days = {
            0 : "Sunday",
            1 : "Monday",
            2 : "Tuesday",
            3 : "Wednesday",
            4 : "Thursday",
            5 : "Friday",
            6 : "Saturday"
        }
        employee_info = self.env['hr.employee'].sudo().search([('id', '=', employee_id)])
        resource_calendar_ids = employee_info.resource_calendar_id
        
        _logger.info('--------------------')
        delta = from_date - to_date       
        for i in range(delta.days + 1):
            day = from_date + timedelta(days=i)
            _logger.info(day)
        # for resource_calendar_id in resource_calendar_ids.attendance_ids:
        #     _logger.info(resource_calendar_id.dayofweek)
        #     _logger.info(resource_calendar_id.day_period)
        #     _logger.info(resource_calendar_id.hour_from)
        #     _logger.info(resource_calendar_id.hour_to)
        _logger.info('--------------------')
