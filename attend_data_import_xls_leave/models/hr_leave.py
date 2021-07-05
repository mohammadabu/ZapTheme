# -*- coding: utf-8 -*-
from odoo import api, models, fields, exceptions, _
import logging
import base64
# import datetime
from datetime import datetime, date, timedelta, time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.base.models.res_partner import _tz_get
import pytz
from xlrd import open_workbook
import tempfile
_logger = logging.getLogger(__name__)
import pandas as pd
import re
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from collections import namedtuple
from pytz import timezone, UTC
DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')
class ImportHrLeave(models.Model):

    _inherit = 'hr.leave'



    def remove_finish_import_crons(self):
        master_partners = self.env['import.leave.master'].search(
            ['|', ('status', '=', 'imported'), ('status', '=', 'failed')])
        # Remove completed crons
        for master_part in master_partners:
            if master_part.cron_id:
                master_part.cron_id.unlink()
        # Remove the Import status lines
        imported_master_part = self.env['import.leave.master'].search(
            [('status', '=', 'imported')])
        imported_master_part.unlink()
    @api.model
    def getRequestDate(self,employee_id,request_date_from,request_date_to):
        employee_info = self.env['hr.employee'].sudo().search([('id','=',employee_id)])
        resource_calendar_id = employee_info.resource_calendar_id or self.env.company.resource_calendar_id
        domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
        attendances = self.env['resource.calendar.attendance'].read_group(domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'week_type', 'dayofweek', 'day_period'], ['week_type', 'dayofweek', 'day_period'], lazy=False)
        attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))
        default_value = DummyAttendance(0, 0, 0, 'morning', False)
        # request_date_from = datetime(2020, 5, 17)
        # request_date_to = datetime(2020, 5, 23)    
        attendance_from = next((att for att in attendances if int(att.dayofweek) >= request_date_from.weekday()), attendances[0] if attendances else default_value)
        attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= request_date_to.weekday()), attendances[-1] if attendances else default_value)
        hour_from = float_to_time(attendance_from.hour_from)
        hour_to = float_to_time(attendance_to.hour_to)
        tz = self.env.user.company_id.resource_calendar_id.tz or self.env.user.tz or 'UTC'
        date_from = timezone(tz).localize(datetime.combine(request_date_from, hour_from)).replace(tzinfo=None)
        date_to = timezone(tz).localize(datetime.combine(request_date_to, hour_to)).replace(tzinfo=None)
        list_arr = []
        list_arr['date_from'] = date_from
        list_arr['date_to'] = date_to
        return list_arr 

    def import_data(self, part_master_id=False):
        if part_master_id:
            part_master = self.env[
                'import.leave.master'].browse(part_master_id)
            total_success_import_record = 0
            total_failed_record = 0
            list_of_failed_record = ''
            datafile = part_master.file
            file_name = str(part_master.filename)
            _logger.info('part_master.filename')
            _logger.info(file_name)
            leave_obj = self.env['hr.leave']
            try:
                if not datafile or not \
                        file_name.lower().endswith(('.xls', '.xlsx')):
                    list_of_failed_record += "Please Select an .xls file to Import."
                    _logger.error(
                        "Please Select an .xls file to Import.")
                _logger.info('part_master.filename')
                _logger.info(part_master.type)        
                if part_master.type == 'xlsx':
                    if not datafile or not file_name.lower().endswith(('.xls', '.xlsx')):
                        list_of_failed_record += "Please Select an .xls or its compatible file to Import."
                        _logger.error(
                            "Please Select an .xls or its compatible file to Import.")
                    
                    temp_path = tempfile.gettempdir()
                    file_data = base64.decodestring(datafile)
                    
                    fp = open(temp_path + '/xsl_file.xls', 'wb+')
                    fp.write(file_data)
                    fp.close()
                    wb = open_workbook(temp_path + '/xsl_file.xls')
                    _logger.info("attendances")
                    _logger.info(date_from)
                    _logger.info(date_to)
                    data_list = []
                    header_list = []
                    headers_dict = {}
                    for sheet in wb.sheets():
                        # _logger.info(sheet.nrows)
                        first_row = False
                        emp_num_row = 0
                        type_leave_row = 0
                        duration_row = 0
                        start_date_row = 0
                        end_date_row = 0
                        for rownum in range(sheet.nrows):
                            item = sheet.row_values(rownum)                            
                            check_emp_num = 0
                            check_type_leave = 0
                            check_duration = 0
                            check_start_date = 0
                            check_end_date = 0
                            for idx1,item1 in enumerate(item):
                                if str(item1).strip() == "رقم الموظف":
                                    emp_num_row = idx1
                                    check_emp_num = 1
                                if str(item1).strip() == "نوع الإجازة":
                                    type_leave_row = idx1
                                    check_type_leave = 1
                                if str(item1).strip() == "المدة":
                                    duration_row = idx1 
                                    check_duration = 1
                                if str(item1).strip() == "البداية":
                                    start_date_row = idx1 
                                    check_start_date = 1
                                if str(item1).strip() == "النهاية":
                                    end_date_row = idx1
                                    check_end_date = 1
                                if  check_emp_num == 1 and  check_type_leave == 1 and  check_duration == 1 and check_start_date == 1 and  check_end_date == 1:     
                                    first_row = rownum
                            if  first_row != False:
                                break    
                        for rownum1 in range(sheet.nrows): 
                            item_y = sheet.row_values(rownum1)           
                            if rownum1 > first_row:
                                # _logger.info("----------------------------------")
                                emp_num =  item_y[emp_num_row]
                                type_leave = item_y[type_leave_row]
                                duration = item_y[duration_row]
                                start_date = item_y[start_date_row]
                                end_date = item_y[end_date_row]
                                if emp_num != "" and duration != "":
                                    valid_start_date = (start_date - 25569) * 86400.0
                                    valid_start_date = datetime.utcfromtimestamp(valid_start_date)
                                    valid_start_date = str(valid_start_date).split(' ')
                                    valid_start_date = valid_start_date[0].replace("-","/",3)
                                    valid_end_date = (end_date - 25569) * 86400.0
                                    valid_end_date = datetime.utcfromtimestamp(valid_end_date)
                                    valid_end_date = str(valid_end_date).split(' ')
                                    valid_end_date = valid_end_date[0].replace("-","/",3)
                                    employee_info = self.env['hr.employee'].sudo().search([('id','=',employee_id)])

                                # _logger.info("----------------------------------")
            except Exception as e:
                list_of_failed_record += str(e)
                _logger.info("--------------------------------------------")
                _logger.info("list_of_failed_record")
                _logger.info(list_of_failed_record)
                _logger.info("--------------------------------------------")


        #     try:
        #         file_data = base64.b64encode(
        #             list_of_failed_record.encode('utf-8'))
        #         part_master.status = 'imported'
        #         datetime_object = datetime.strptime(
        #             str(part_master.create_date), '%Y-%m-%d %H:%M:%S.%f')
        #         start_date = datetime.strftime(
        #             datetime_object, DEFAULT_SERVER_DATETIME_FORMAT)
        #         self._cr.commit()
        #         now_time = datetime.now()
        #         user_tz = self.env.user.tz or str(pytz.utc)
        #         local = pytz.timezone(user_tz)
        #         start_date_in_user_tz = datetime.strftime(pytz.utc.localize(
        #             datetime.strptime(str(start_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
        #             local), DEFAULT_SERVER_DATETIME_FORMAT)
        #         end_date_in_user_tz = datetime.strftime(pytz.utc.localize(
        #             now_time).astimezone(local),
        #             DEFAULT_SERVER_DATETIME_FORMAT)
        #         self.env['import.attendances.history'].create({
        #             'total_success_count': total_success_import_record,
        #             'total_failed_count': total_failed_record,
        #             'file': file_data,
        #             'file_name': 'report_importazione.txt',
        #             'type': part_master.type,
        #             'import_file_name': part_master.filename,
        #             'start_date': start_date_in_user_tz,
        #             'end_date': end_date_in_user_tz,
        #             'operation': part_master.operation,
        #         })
        #         if part_master.user_id:
        #             message = "Import process is completed. Check in Imported attendances History if all the attendances have" \
        #                       " been imported correctly. </br></br> Imported File: %s </br>" \
        #                       "Imported by: %s" % (
        #                           part_master.filename, part_master.user_id.name)
        #             part_master.user_id.notify_partner_info(
        #                 message, part_master.user_id, sticky=True)
        #         self._cr.commit()
        #     except Exception as e:
        #         part_master.status = 'failed'
        #         _logger.error(e)
        #         self._cr.commit()






    # def _onchange_request_parameters(self):
    #     if not self.request_date_from:
    #         self.date_from = False
    #         return

    #     if self.request_unit_half or self.request_unit_hours:
    #         self.request_date_to = self.request_date_from

    #     if not self.request_date_to:
    #         self.date_to = False
    #         return

    #     resource_calendar_id = self.employee_id.resource_calendar_id or self.env.company.resource_calendar_id
    #     domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
    #     attendances = self.env['resource.calendar.attendance'].read_group(domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'week_type', 'dayofweek', 'day_period'], ['week_type', 'dayofweek', 'day_period'], lazy=False)

    #     # Must be sorted by dayofweek ASC and day_period DESC
    #     attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))

    #     default_value = DummyAttendance(0, 0, 0, 'morning', False)
