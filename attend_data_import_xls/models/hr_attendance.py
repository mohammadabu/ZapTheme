from odoo import api, models
import logging
import base64
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from xlrd import open_workbook
import tempfile
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'hr.attendance'

    def remove_finish_import_crons(self):
        master_partners = self.env['import.attendances.master'].search(
            ['|', ('status', '=', 'imported'), ('status', '=', 'failed')])
        # Remove completed crons
        for master_part in master_partners:
            if master_part.cron_id:
                master_part.cron_id.unlink()
        # Remove the Import status lines
        imported_master_part = self.env['import.attendances.master'].search(
            [('status', '=', 'imported')])
        imported_master_part.unlink()
    @api.model
    def convert24(self,str1):
        time_arr = {
            "00":12,
            "01":13,
            "02":14,
            "03":15,
            "04":16,
            "05":17,
            "06":18,
            "07":19,
            "08":20,
            "09":21,
            "10":22,
            "11":23,
            "12":00
        }
        check_in_time = str1[0]
        check_in_time = check_in_time.replace("\u200f","")
        check_in_time_split = check_in_time.split(":")
        hours = check_in_time_split[0]
        minutes = check_in_time_split[1]
        check_in_zone = str1[1]
        if check_in_zone == "ص" and hours == "12":
            return "00:"+minutes
        elif check_in_zone == "ص":
            return hours+":"+ minutes
        elif check_in_zone == "م" and hours == "12":
            return "12"+":"+ minutes
        else:
            
            # _logger.info(time_arr[hours])
            # _logger.info(minutes)
            return str(time_arr[hours]) + ":" + minutes          
    def import_data(self, part_master_id=False):
        if part_master_id:
            part_master = self.env[
                'import.attendances.master'].browse(part_master_id)
            total_success_import_record = 0
            total_failed_record = 0
            list_of_failed_record = ''
            datafile = part_master.file
            file_name = str(part_master.filename)
            partner_obj = self.env['res.partner']
            state_obj = self.env['res.country.state']
            country_obj = self.env['res.country']
            try:
                if not datafile or not \
                        file_name.lower().endswith(('.xls', '.xlsx')):
                    list_of_failed_record += "Please Select an .xls file to Import."
                    _logger.error(
                        "Please Select an .xls file to Import.")
                if part_master.type == 'xlsx':
                    if not datafile or not file_name.lower().endswith(('.xls', '.xlsx',)):
                        list_of_failed_record += "Please Select an .xls or its compatible file to Import."
                        _logger.error(
                            "Please Select an .xls or its compatible file to Import.")
                    temp_path = tempfile.gettempdir()
                    file_data = base64.decodestring(datafile)
                    fp = open(temp_path + '/xsl_file.xls', 'wb+')
                    fp.write(file_data)
                    fp.close()
                    wb = open_workbook(temp_path + '/xsl_file.xls')
                    data_list = []
                    header_list = []
                    headers_dict = {}
                    for sheet in wb.sheets():
                        _logger.info(sheet.nrows)
                    #     # Sales data xlsx
                        first_row = 0
                        emp_name_row = 0
                        date_row = 0
                        check_in_row = 0
                        check_out_row = 0
                        for rownum in range(sheet.nrows):
                            # _logger.info(rownum)
                            # _logger.info(sheet.row_values(rownum))
                            item = sheet.row_values(rownum)
                            if "اسم الموظف" in item and "التاريخ" in item and "وقت دخول" in item and "وقت الخروج" in item:
                                first_row = rownum
                                for idx1,item1 in enumerate(item):
                                    if item1 == "اسم الموظف":
                                        emp_name_row = idx1
                                    if item1 == "التاريخ":
                                        date_row = idx1
                                    if item1 == "وقت دخول":
                                        check_in_row = idx1
                                    if item1 == "وقت الخروج":
                                        check_out_row = idx1
                                break    

                        for rownum1 in range(sheet.nrows): 
                            item_y = sheet.row_values(rownum1)           
                            if rownum1 > first_row:
                                emp_name =  item_y[emp_name_row]
                                date = item_y[date_row] 
                                check_in = item_y[check_in_row]     
                                check_out = item_y[check_out_row] 
                                full_date_check_in = False
                                full_date_check_out = False
                                _logger.info("------------------------")
                                if emp_name != "" and (check_in != "" or check_out != ""):  
                                    if check_in:
                                        split_check_in = check_in.split(" ")
                                        if len(split_check_in) > 1:
                                            try:
                                                date = date.replace("/","-",3)
                                                new_time = self.pool.get("hr.attendance").convert24(self,split_check_in)
                                                new_time = new_time.replace("\u200f","")
                                                full_date_time = date + " " + new_time + ":00"
                                                # full_date_time_obj = datetime.strptime(full_date_time, '%Y-%m-%d %H:%M:%S')
                                                full_date_check_in = datetime.strptime(full_date_time, '%Y-%m-%d %H:%M:%S')
                                                # _logger.info(full_date_time_obj)
                                            except Exception as e:
                                                _logger.info("----error in------")   
                                                _logger.info(e) 
                                    if check_out:
                                        split_check_out = check_out.split(" ")
                                        if len(split_check_out) > 1:  
                                            try:
                                                date = date.replace("/","-",3)
                                                new_time = self.pool.get("hr.attendance").convert24(self,split_check_out)
                                                full_date_time = date + " " + new_time + ":00"
                                                # full_date_time_obj = datetime.strptime(full_date_time, '%Y-%m-%d %H:%M:%S')
                                                full_date_check_out = datetime.strptime(full_date_time, '%Y-%m-%d %H:%M:%S')
                                            except Exception as e:
                                                _logger.info("----error out------")    
                                                _logger.info(e)   
                                if  full_date_check_in != False or full_date_check_out != False:
                                    _logger.info(full_date_check_in)
                                    _logger.info(full_date_check_out)                 
                                _logger.info("------------------------")                         
                                                
                    #         if rownum == 0:
                    #             header_list = [
                    #                 x for x in sheet.row_values(rownum)]
                    #             headers_dict = {
                    #                 'name': header_list.index('Name'),
                    #                 'mobile': header_list.index('Mobile'),
                    #                 'phone': header_list.index('Phone'),
                    #                 'email': header_list.index('Email'),
                    #                 'vat': header_list.index('Vat'),
                    #                 'street': header_list.index('Street'),
                    #                 'street2': header_list.index('Street2'),
                    #                 'city': header_list.index('City'),
                    #                 'company_type': header_list.index('Company Type'),
                    #                 'website': header_list.index('Website'),
                    #                 'state': header_list.index('State'),
                    #                 'country': header_list.index('Country'),
                    #                 'zip': header_list.index('ZIP')
                    #             }
                    #         if rownum >= 1:
                    #             data_list.append(sheet.row_values(rownum))
                    #     count = 1
                    #     for row in data_list:
                    #         try:
                    #             count += 1

                    #             state = state_obj.search(
                    #                 [('name', '=', row[headers_dict['state']])])
                    #             country = country_obj.search(
                    #                 [('name', '=', row[headers_dict['country']])])

                    #             partner_vals = {
                    #                 'name': row[headers_dict['name']],
                    #                 'phone': row[headers_dict['phone']] or '',
                    #                 'mobile': row[headers_dict['mobile']] or '',
                    #                 'email': row[headers_dict['email']] or '',
                    #                 'vat': row[headers_dict['vat']] or '',
                    #                 'street': row[headers_dict['street']] or '',
                    #                 'street2': row[headers_dict['street2']] or '',
                    #                 'city': row[headers_dict['city']] or '',
                    #                 'state_id': state.id or '',
                    #                 'country_id': country.id or '',
                    #                 'company_type': row[headers_dict['company_type']],
                    #                 'website': row[headers_dict['website']] or '',
                    #                 'zip': row[headers_dict['zip']] or '',
                    #             }
                    #             if part_master.operation == 'create':
                    #                 order_id = partner_obj.create(
                    #                     partner_vals)
                    #             else:
                    #                 order_id = self.env['res.partner'].search(
                    #                     [('name', '=', row[headers_dict['name']])], limit=1)
                    #                 if not order_id:
                    #                     order_id = partner_obj.create(
                    #                         partner_vals)
                    #                 else:
                    #                     order_id.write(partner_vals)
                    #             total_success_import_record += 1
                    #         except Exception as e:
                    #             total_failed_record += 1
                    #             list_of_failed_record += row
                    #             _logger.error("Error at %s" % str(row))
            except Exception as e:
                list_of_failed_record += str(e)
            # try:
            #     file_data = base64.b64encode(
            #         list_of_failed_record.encode('utf-8'))
            #     part_master.status = 'imported'
            #     datetime_object = datetime.strptime(
            #         str(part_master.create_date), '%Y-%m-%d %H:%M:%S.%f')
            #     start_date = datetime.strftime(
            #         datetime_object, DEFAULT_SERVER_DATETIME_FORMAT)
            #     self._cr.commit()
            #     now_time = datetime.now()
            #     user_tz = self.env.user.tz or str(pytz.utc)
            #     local = pytz.timezone(user_tz)
            #     start_date_in_user_tz = datetime.strftime(pytz.utc.localize(
            #         datetime.strptime(str(start_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
            #         local), DEFAULT_SERVER_DATETIME_FORMAT)
            #     end_date_in_user_tz = datetime.strftime(pytz.utc.localize(
            #         now_time).astimezone(local),
            #         DEFAULT_SERVER_DATETIME_FORMAT)
            #     self.env['import.part.history'].create({
            #         'total_success_count': total_success_import_record,
            #         'total_failed_count': total_failed_record,
            #         'file': file_data,
            #         'file_name': 'report_importazione.txt',
            #         'type': part_master.type,
            #         'import_file_name': part_master.filename,
            #         'start_date': start_date_in_user_tz,
            #         'end_date': end_date_in_user_tz,
            #         'operation': part_master.operation,
            #     })
            #     if part_master.user_id:
            #         message = "Import process is completed. Check in Imported partner History if all the partners have" \
            #                   " been imported correctly. </br></br> Imported File: %s </br>" \
            #                   "Imported by: %s" % (
            #                       part_master.filename, part_master.user_id.name)
            #         part_master.user_id.notify_partner_info(
            #             message, part_master.user_id, sticky=True)
            #     self._cr.commit()
            # except Exception as e:
            #     part_master.status = 'failed'
            #     _logger.error(e)
            #     self._cr.commit()
