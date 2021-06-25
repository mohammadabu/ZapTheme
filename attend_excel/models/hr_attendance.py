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

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    employees = fields.Many2many('hr.employee')
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
    def getTotal_diff_hours(self,total_exist_hours,total_hours):
        total_hours_split = total_hours.split(':')
        total_hours = total_hours_split[0] + ":" + total_hours_split[1]
        try:
            tdelta = datetime.strptime(total_hours, '%H:%M') - datetime.strptime(total_exist_hours, '%H:%M')
            if '-1 day' in str(tdelta):
                return False 
            else:
                tdelta_split = str(tdelta).split(':')
                return tdelta_split[0] + ":" + tdelta_split[1]      
            # _logger.info(total_exist_hours)   
            # _logger.info(total_hours)
            # _logger.info(str(tdelta))
        except:
            _logger.info('error')
            _logger.info(total_exist_hours)   
            _logger.info(total_hours)

    @api.model
    def addHourToHour(self,total_hours,hour):
        total_hours = total_hours.split(':')
        tdelta_total_hours = int(total_hours[0])
        tdelta_total_min = int(total_hours[1])
        hour = hour.split(':')
        tdelta_hour = int(hour[0])
        tdelta_min = int(hour[1])
        final_total_hour = tdelta_total_hours + tdelta_hour
        final_total_min = tdelta_total_min + tdelta_min
        if final_total_min >= 60:
            final_total_hour = final_total_hour + 1
            final_total_min = final_total_min - 60            

        return str(final_total_hour) + ":" + str(final_total_min)

    @api.model
    def get_total_hours(self,employee_id,day):
        # _logger.info('-------after total hours---------')
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
                str_tdelta = str(tdelta)
                if total_hours != False:
                    total_hours =  self.pool.get("wizard.attendance.history.excel").addHourToHour(self,total_hours,str_tdelta)
                else:
                    total_hours = str_tdelta
        return total_hours

    @api.model
    def get_employee_attendance(self,employee_id,from_date,to_date):
        table_excel = {}
        employee_info = self.env['hr.employee'].sudo().search([('id', '=', employee_id)])
        id_number = employee_info.employee_id
        employee_name = employee_info.name
        resource_calendar_ids = employee_info.resource_calendar_id
        all_employee_attendance =  self.pool.get("wizard.attendance.history.excel").get_absent_days(self,employee_id,from_date,to_date)
        # _logger.info('all_employee_attendance')
        # _logger.info(all_employee_attendance)
        if all_employee_attendance['absent_days'] == False:
            all_employee_attendance['absent_days'] = 0
        if all_employee_attendance['absent_days_without_leave'] == False:
            all_employee_attendance['absent_days_without_leave'] = 0
        if all_employee_attendance['late_hours'] == False:
            all_employee_attendance['late_hours'] = 0        
        table_excel = {}
        table_excel['id_number'] = id_number
        table_excel['employee_name'] = employee_name
        table_excel['absent_days'] = all_employee_attendance['absent_days']
        table_excel['absent_days_without_leave'] = all_employee_attendance['absent_days_without_leave']
        table_excel['late_hours'] = all_employee_attendance['late_hours']
        return table_excel

    @api.model
    def get_absent_days(self,employee_id,from_date,to_date):
        absent_days = False
        absent_days_without_leave = False
        late_hours = False
        days = ["Monday", "Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_exist = []
        employee_info = self.env['hr.employee'].sudo().search([('id', '=', employee_id)])
        resource_calendar_ids = employee_info.resource_calendar_id
        for resource_calendar_id in resource_calendar_ids.attendance_ids:
            days_title = days[int(resource_calendar_id.dayofweek)]
            if days_title not in day_exist:
                day_exist.append(days_title)
        # _logger.info(day_exist)
        # from_date =  datetime.strptime('2021-06-23', '%Y-%m-%d')
        # to_date =  datetime.strptime('2021-06-30', '%Y-%m-%d')
        from_date =  datetime.strptime(str(from_date), '%Y-%m-%d')
        to_date =  datetime.strptime(str(to_date), '%Y-%m-%d')
        delta = to_date - from_date       
        # _logger.info(delta.days) 
        for i in range(delta.days + 1):
            day = from_date + timedelta(days=i)
            date_from = day
            date_to = date_from + timedelta(hours=23)
            day = day.strftime("%A")
            if day in day_exist:
                attendance_info = self.env['hr.attendance'].sudo().search(['&',('check_in', '>=', date_from),'&',('check_in', '<=', date_to),('employee_id','=',employee_id)])
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
                        # _logger.info('-------total hours---------')
                        # _logger.info(date_from)
                        # _logger.info(date_to)
                        # _logger.info(attendance_info)
                        total_hours =  self.pool.get("wizard.attendance.history.excel").get_total_hours(self,employee_id,day)
                        # _logger.info('-------attendance_info---------')
                        # _logger.info(day)
                        total_exist_hours = False
                        for attendance in attendance_info:
                            if attendance.check_out != False:
                                tdelta_check = datetime.strptime(str(attendance.check_out), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(attendance.check_in), '%Y-%m-%d %H:%M:%S')
                                if total_exist_hours != False:
                                    total_exist_hours =  self.pool.get("wizard.attendance.history.excel").addHourToHour(self,total_exist_hours,str(tdelta_check))
                                else:
                                    tdelta_check_split = str(tdelta_check).split(':') 
                                    total_exist_hours = tdelta_check_split[0] + ":" + tdelta_check_split[1]
                                # _logger.info('------------------')
                                # _logger.info(attendance.check_in)
                                # _logger.info(attendance.check_out)
                                # _logger.info(str(tdelta_check))
                                # _logger.info('------------------')
                        # _logger.info(total_exist_hours)   
                        # _logger.info(total_hours)    
                        total_diff_hours =  self.pool.get("wizard.attendance.history.excel").getTotal_diff_hours(self,total_exist_hours,total_hours) 
                        if total_diff_hours != False: #Not OverTime
                            if late_hours != False:
                                late_hours =  self.pool.get("wizard.attendance.history.excel").addHourToHour(self,late_hours,total_diff_hours)
                            else:
                                late_hours = total_diff_hours
                            # _logger.info(total_diff_hours)
                        # _logger.info('-------attendance_info---------')    
        if  late_hours != False:
            late_hours_split = late_hours.split(':')     
            late_hours_min = late_hours_split[1]
            if len(late_hours_min) <= 1:
                if late_hours_min == "0":
                    late_hours = late_hours_split[0] + ":00"
                else:
                    late_hours = late_hours_split[0] + ":0"+ late_hours_min
        absent_days_arr =  {}
        absent_days_arr['absent_days'] = absent_days
        absent_days_arr['absent_days_without_leave'] = absent_days_without_leave
        absent_days_arr['late_hours'] = late_hours               
        # _logger.info(absent_days)
        # _logger.info(absent_days_without_leave)
        # _logger.info(late_hours) 
        return absent_days_arr

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        lines = self.browse(data['ids'])
        employees = lines.employees
        from_date = lines.from_date
        to_date = lines.to_date
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Attendance Info')

        row_format = workbook.add_format({'color': 'black','border': 1,'font_size':11})
        row_format.set_text_wrap()
        row_format.set_align('center')
        row_format.set_align('vcenter')

        column_format = workbook.add_format({'color': 'white','bg_color':'green','border': 1,'font_size':14})
        column_format.set_text_wrap()
        column_format.set_align('center')
        column_format.set_align('vcenter')
        cell_format = workbook.add_format({'font_size':12})
        cell_format.set_align('center')
        cell_format.set_align('vcenter')
        cell_format.set_text_wrap()
        sheet.merge_range('C1:I4', "", cell_format)
        header_excel = "التقرير الشامل - أيام الغياب وساعات العمل"
        header_excel += " \n"
        date_from_hijri = "1442/09/20"
        date_from = datetime.strptime(str(from_date), '%Y/%m/%d')
        header_excel += (u'من  %s') % (date_from_hijri + " - " + date_from)
        header_excel += " \n"
        date_to_hijri = "1442/09/20"
        date_to = "2021/05/02"
        header_excel += (u'الى  %s') % (date_to_hijri + " - " + date_to)
        sheet.write('C1',header_excel,cell_format)
        sheet.set_column('A:A', 1)
        sheet.set_column('B:B', 1)
        sheet.set_column('C:C', 9)
        sheet.set_column('D:D', 9)
        sheet.set_column('E:E', 18)
        sheet.set_column('F:F', 18)
        sheet.set_column('G:G', 18)
        sheet.set_column('H:H', 18)
        sheet.set_column('I:I', 5)
        sheet.write(4, 2, 'ساعات التأخر النهائية',column_format)
        sheet.write(4, 3, 'ساعات التأخر',column_format)
        sheet.write(4, 4, 'أيام الخروج بدون اذن',column_format)
        sheet.write(4, 5, 'أيام الغياب',column_format)
        sheet.write(4, 6, 'اسم الموظف',column_format)
        sheet.write(4, 7, 'رقم الهوية',column_format)
        sheet.write(4, 8, 'م',column_format)
        if len(employees) <= 0:
            employees = self.env['hr.employee'].sudo().search([])
        count_rows = 1
        for employee in employees:
            all_employee_attendance =  self.pool.get("wizard.attendance.history.excel").get_employee_attendance(self,employee.id,from_date,to_date)
            try:
                sheet.write(4 + count_rows, 8, count_rows,row_format)
                sheet.write(4 + count_rows, 7, all_employee_attendance['id_number'],row_format)
                sheet.write(4 + count_rows, 6, all_employee_attendance['employee_name'],row_format)
                sheet.write(4 + count_rows, 5, all_employee_attendance['absent_days'],row_format)
                sheet.write(4 + count_rows, 4, all_employee_attendance['absent_days_without_leave'],row_format)
                sheet.write(4 + count_rows, 3, all_employee_attendance['late_hours'],row_format)
                sheet.write(4 + count_rows, 2, '',row_format)
                count_rows = count_rows + 1
            except:
                _logger.info(all_employee_attendance)
        # _logger.info(from_date)
        # _logger.info(to_date)
        # _logger.info(employees)


        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
