import time
from datetime import date, datetime,timedelta
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
import pytz
import json
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
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'wizard.attendance.history.excel',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Current Attendance History',
                    }
        }

    @api.model
    def get_total_hours(self,employee_id,day):
        _logger.info('-------after total hours---------')
        total_hours = False
        days = ["Monday", "Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        employee_info = self.env['hr.employee'].sudo().search([('id', '=', employee_id)])
        resource_calendar_ids = employee_info.resource_calendar_id
        for resource_calendar_id in resource_calendar_ids.attendance_ids:
            days_title = days[int(resource_calendar_id.dayofweek)]
            if days_title == day:
                hour_from = float_to_time(resource_calendar_id.hour_from)
                hour_to = float_to_time(resource_calendar_id.hour_to)
                tdelta = datetime.strptime(str(hour_to), '%H:%M:%S') - datetime.strptime(str(hour_from), '%H:%M:%S')
                _logger.info(resource_calendar_id.dayofweek)
                _logger.info(resource_calendar_id.day_period)
                _logger.info(hour_from)
                _logger.info(hour_to)
                _logger.info(tdelta)
                if total_hours != False:
                    total_hours = datetime.strptime(str(total_hours), '%H:%M:%S') + datetime.strptime(str(tdelta), '%H:%M:%S')
                else:
                    total_hours = datetime.strptime(str(tdelta), '%H:%M:%S')
        _logger.info(total_hours)            
        _logger.info('----------------')



    @api.model
    def get_employee_attendance(self,count_employee,employee_id,from_date,to_date):
        table_excel = {}
        # employee_id = 125
        # from_date = '2021-06-23'
        # to_date = '2021-06-30'
        _logger.info(employee_id)
        _logger.info(from_date)
        _logger.info(to_date)
        employee_info = self.env['hr.employee'].sudo().search([('id', '=', employee_id)])
        id_number = employee_info.employee_id
        employee_name = employee_info.employee_id
        resource_calendar_ids = employee_info.resource_calendar_id
        all_employee_attendance =  self.pool.get("wizard.attendance.history.excel").get_absent_days(self,employee_id,from_date,to_date)
        # table_excel[count_employee] = {}
        # table_excel[count_employee]['id_number'] = id_number
        # table_excel[count_employee]['employee_name'] = employee_name
        # table_excel[count_employee]['employee_name'] = employee_name

    @api.model
    def get_absent_days(self,employee_id,from_date,to_date):
        absent_days = False
        absent_days_without_leave = False
        days = ["Monday", "Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_exist = []
        employee_info = self.env['hr.employee'].sudo().search([('id', '=', employee_id)])
        resource_calendar_ids = employee_info.resource_calendar_id
        for resource_calendar_id in resource_calendar_ids.attendance_ids:
            days_title = days[int(resource_calendar_id.dayofweek)]
            if days_title not in day_exist:
                day_exist.append(days_title)
        # _logger.info(day_exist)
        from_date =  datetime.strptime('2021-06-23', '%Y-%m-%d')
        to_date =  datetime.strptime('2021-06-30', '%Y-%m-%d')
        delta = to_date - from_date       
        # _logger.info(delta.days) 
        for i in range(delta.days + 1):
            day = from_date + timedelta(days=i)
            date_from = day
            date_to = date_from + timedelta(hours=23)
            day = day.strftime("%A")
            if day in day_exist:
                attendance_info = self.env['hr.attendance'].sudo().search([('check_in', '>=', date_from),('check_in', '<=', date_to)])
                leave_info = self.env['hr.leave'].sudo().search(['&',('request_date_from', '=', date_from),'&',('state','=','validate'),('employee_id','=',employee_id)])
                # _logger.info('----------------')
                # _logger.info(day)
                # _logger.info(date_from)
                # _logger.info(date_to)
                # _logger.info(attendance_info)
                # _logger.info(leave_info)
                # _logger.info('----------------')
                if len(attendance_info) <= 0:
                    if len(leave_info) > 0:
                        if absent_days != False:
                            absent_days = absent_days + ',' + str(date_from.strftime("%m/%d"))
                        else:
                            absent_days = str(date_from.strftime("%m/%d"))   
                    else:
                        if absent_days_without_leave != False:
                            absent_days_without_leave = absent_days_without_leave + ',' + str(date_from.strftime("%m/%d"))
                        else:
                            absent_days_without_leave = str(date_from.strftime("%m/%d"))  
                else:
                    if len(leave_info) <= 0:
                        _logger.info('-------before total hours---------')
                        # _logger.info(date_from)
                        # _logger.info(date_to)
                        _logger.info(day)
                        _logger.info(attendance_info)
                        _logger.info('----------------')
                        total_hours =  self.pool.get("wizard.attendance.history.excel").get_total_hours(self,employee_id,day)

        # _logger.info('--------------------')
        # _logger.info(absent_days)
        # _logger.info(absent_days_without_leave)        
        # for resource_calendar_id in resource_calendar_ids.attendance_ids:
        #     _logger.info(resource_calendar_id.dayofweek)
        #     _logger.info(resource_calendar_id.day_period)
        #     _logger.info(resource_calendar_id.hour_from)
        #     _logger.info(resource_calendar_id.hour_to)
        # _logger.info('--------------------')

    





    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        lines = self.browse(data['ids'])
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Attendance Info')
        red = workbook.add_format({'color': 'red'})
        column_format = workbook.add_format({'color': 'white','bg_color':'green','border': 1,'font_size':14})
        column_format.set_text_wrap()
        column_format.set_align('center')
        column_format.set_align('vcenter')
        cell_format = workbook.add_format({'border': 1})
        cell_format.set_align('center')
        cell_format.set_align('vcenter')
        sheet.merge_range('C1:I3', "", cell_format)
        sheet.write('C1',""" التقرير الشامل - أيام الغياب وساعات العمل
            من 1442/09/20-2021/05/02 الى 1442/10/19-2021/05/31
            ‏  """,cell_format)
        sheet.set_column('A:A', 1)
        sheet.set_column('B:B', 1)
        sheet.set_column('C:C', 9)
        sheet.set_column('D:D', 9)
        sheet.set_column('E:E', 18)
        sheet.set_column('F:F', 18)
        sheet.set_column('G:G', 18)
        sheet.set_column('H:H', 18)
        sheet.set_column('I:I', 5)
        sheet.write(3, 2, 'ساعات التأخر النهائية',column_format)
        sheet.write(3, 3, 'ساعات التأخر',column_format)
        sheet.write(3, 4, 'أيام الخروج بدون اذن',column_format)
        sheet.write(3, 5, 'أيام الغياب',column_format)
        sheet.write(3, 6, 'اسم الموظف',column_format)
        sheet.write(3, 7, 'رقم الهوية',column_format)
        sheet.write(3, 8, 'م',column_format)
        employees = lines.employees
        from_date = lines.from_date
        to_date = lines.to_date
        count_employee = 0
        for employee in employees:
            all_employee_attendance =  self.pool.get("wizard.attendance.history.excel").get_employee_attendance(self,count_employee,employee.id,from_date,to_date)
            count_employee = count_employee + 1
            # _logger.info(employee.id)
            # _logger.info(from_date)
            # _logger.info(to_date)


        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
