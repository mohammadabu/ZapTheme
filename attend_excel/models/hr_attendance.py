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
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'wizard.attendance.history.excel',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Current Attendance History',
                    }
        }
    @api.model
    def get_employee_attendance(self, data):
        employees = data.employees
        from_date = data.from_date
        to_date = data.to_date
        _logger.info('--------------------')
        _logger.info(employees)
        _logger.info(from_date)
        _logger.info(to_date)
        _logger.info('--------------------')

    def get_xlsx_report(self, data, response):
        # output = io.BytesIO()
        lines = self.browse(data['ids'])
        all_employee_attendance =  self.pool.get("wizard.attendance.history.excel").get_employee_attendance(self,lines)
#         workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#         sheet = workbook.add_worksheet('Attendance Info')
#         red = workbook.add_format({'color': 'red'})
#         blue = workbook.add_format({'color': 'blue'})
#         cell_format = workbook.add_format({'align': 'center',
#                                    'valign': 'vcenter',
#                                    'border': 1})
#         sheet.merge_range('C1:I3', "", cell_format)
#         sheet.write('C1',""" التقرير الشامل - أيام الغياب وساعات العمل
# من 1442/09/20-2021/05/02 الى 1442/10/19-2021/05/31
# ‏  """,cell_format)
#         sheet.set_column('A:A', 1)
#         sheet.set_column('B:B', 1)
#         sheet.set_column('C:C', 9)
#         sheet.set_column('D:D', 9)
#         sheet.set_column('E:E', 18)
#         sheet.set_column('F:F', 18)
#         sheet.set_column('G:G', 18)
#         sheet.set_column('H:H', 18)
#         sheet.set_column('I:I', 5)

#         sheet.write(3, 2, 'ساعات التأخر النهائية')
#         sheet.write(3, 3, 'ساعات التأخر')
#         sheet.write(3, 4, 'أيام الخروج بدون اذن')
#         sheet.write(3, 5, 'أيام الغياب')
#         sheet.write(3, 6, 'اسم الموظف')
#         sheet.write(3, 7, 'رقم الهوية')
#         sheet.write(3, 8, 'م')






                           



        # font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
    #     font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
    #     font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
    #     red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
    #     justify = workbook.add_format({'font_size': 12})
    #     format3.set_align('center')
    #     justify.set_align('justify')
    #     format1.set_align('center')
    #     red_mark.set_align('center')
    #     sheet.merge_range(1, 7, 2, 10, 'Product Stock Info', format0)
    #     sheet.merge_range(3, 7, 3, 10, comp, format11)
    #     w_house = ', '
    #     cat = ', '
    #     c = []
    #     d1 = d.mapped('id')
    #     if d1:
    #         for i in d1:
    #             c.append(self.env['product.category'].browse(i).name)
    #         cat = cat.join(c)
    #         sheet.merge_range(4, 0, 4, 1, 'Category(s) : ', format4)
    #         sheet.merge_range(4, 2, 4, 3 + len(d1), cat, format4)
    #     sheet.merge_range(5, 0, 5, 1, 'Warehouse(s) : ', format4)
    #     w_house = w_house.join(get_warehouse[0])
    #     sheet.merge_range(5, 2, 5, 3 + len(get_warehouse[0]), w_house, format4)
    #     user = self.env['res.users'].browse(self.env.uid)
    #     tz = pytz.timezone(user.tz if user.tz else 'UTC')
    #     times = pytz.utc.localize(datetime.datetime.now()).astimezone(tz)
    #     sheet.merge_range('A8:G8', 'Report Date: ' + str(times.strftime("%Y-%m-%d %H:%M %p")), format1)
    #     sheet.merge_range(7, 7, 7, count, 'Warehouses', format1)
    #     sheet.merge_range('A9:G9', 'Product Information', format11)
    #     w_col_no = 6
    #     w_col_no1 = 7
    #     for i in get_warehouse[0]:
    #         w_col_no = w_col_no + 11
    #         sheet.merge_range(8, w_col_no1, 8, w_col_no, i, format11)
    #         w_col_no1 = w_col_no1 + 11
    #     sheet.write(9, 0, 'SKU', format21)
    #     sheet.merge_range(9, 1, 9, 3, 'Name', format21)
    #     sheet.merge_range(9, 4, 9, 5, 'Category', format21)
    #     sheet.write(9, 6, 'Cost Price', format21)
    #     p_col_no1 = 7
    #     for i in get_warehouse[0]:
    #         sheet.write(9, p_col_no1, 'Available', format21)
    #         sheet.write(9, p_col_no1 + 1, 'Virtual', format21)
    #         sheet.write(9, p_col_no1 + 2, 'Incoming', format21)
    #         sheet.write(9, p_col_no1 + 3, 'Outgoing', format21)
    #         sheet.merge_range(9, p_col_no1 + 4, 9, p_col_no1 + 5, 'Net On Hand', format21)
    #         sheet.merge_range(9, p_col_no1 + 6, 9, p_col_no1 + 7, 'Total Sold', format21)
    #         sheet.merge_range(9, p_col_no1 + 8, 9, p_col_no1 + 9, 'Total Purchased', format21)
    #         sheet.write(9, p_col_no1 + 10, 'Valuation', format21)
    #         p_col_no1 = p_col_no1 + 11
    #     prod_row = 10
    #     prod_col = 0
    #     for i in get_warehouse[1]:
    #         get_line = self.get_lines(d, i)
    #         for each in get_line:
    #             sheet.write(prod_row, prod_col, each['sku'], font_size_8)
    #             sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 3, each['name'], font_size_8_l)
    #             sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['category'], font_size_8_l)
    #             sheet.write(prod_row, prod_col + 6, each['cost_price'], font_size_8_r)
    #             prod_row = prod_row + 1
    #         break
    #     prod_row = 10
    #     prod_col = 7
    #     for i in get_warehouse[1]:
    #         get_line = self.get_lines(d, i)
    #         for each in get_line:
    #             if each['available'] < 0:
    #                 sheet.write(prod_row, prod_col, each['available'], red_mark)
    #             else:
    #                 sheet.write(prod_row, prod_col, each['available'], font_size_8)
    #             if each['virtual'] < 0:
    #                 sheet.write(prod_row, prod_col + 1, each['virtual'], red_mark)
    #             else:
    #                 sheet.write(prod_row, prod_col + 1, each['virtual'], font_size_8)
    #             if each['incoming'] < 0:
    #                 sheet.write(prod_row, prod_col + 2, each['incoming'], red_mark)
    #             else:
    #                 sheet.write(prod_row, prod_col + 2, each['incoming'], font_size_8)
    #             if each['outgoing'] < 0:
    #                 sheet.write(prod_row, prod_col + 3, each['outgoing'], red_mark)
    #             else:
    #                 sheet.write(prod_row, prod_col + 3, each['outgoing'], font_size_8)
    #             if each['net_on_hand'] < 0:
    #                 sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['net_on_hand'], red_mark)
    #             else:
    #                 sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['net_on_hand'], font_size_8)
    #                 if each['sale_value'] < 0:
    #                     sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['sale_value'], red_mark)
    #                 else:
    #                     sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['sale_value'], font_size_8)
    #             if each['purchase_value'] < 0:
    #                 sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 9, each['purchase_value'], red_mark)
    #             else:
    #                 sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 9, each['purchase_value'],
    #                                   font_size_8)
    #             if each['total_value'] < 0:
    #                 sheet.write(prod_row, prod_col + 10, each['total_value'], red_mark)
    #             else:
    #                 sheet.write(prod_row, prod_col + 10, each['total_value'], font_size_8_r)
    #             prod_row = prod_row + 1
    #         prod_row = 10
    #         prod_col = prod_col + 11
        # workbook.close()
        # output.seek(0)
        # response.stream.write(output.read())
        # output.close()
