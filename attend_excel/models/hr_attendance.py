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

    # def get_warehouse(self, data):
    #     wh = data.warehouse.mapped('id')
    #     obj = self.env['stock.warehouse'].search([('id', 'in', wh)])
    #     l1 = []
    #     l2 = []
    #     for j in obj:
    #         l1.append(j.name)
    #         l2.append(j.id)
    #     return l1, l2

    # def get_lines(self, data, warehouse):
    #     lines = []
    #     categ_id = data.mapped('id')
    #     if categ_id:
    #         categ_products = self.env['product.product'].search([('categ_id', 'in', categ_id)])

    #     else:
    #         categ_products = self.env['product.product'].search([])
    #     product_ids = tuple([pro_id.id for pro_id in categ_products])
    #     sale_query = """
    #            SELECT sum(s_o_l.product_uom_qty) AS product_uom_qty, s_o_l.product_id FROM sale_order_line AS s_o_l
    #            JOIN sale_order AS s_o ON s_o_l.order_id = s_o.id
    #            WHERE s_o.state IN ('sale','done')
    #            AND s_o.warehouse_id = %s
    #            AND s_o_l.product_id in %s group by s_o_l.product_id"""
    #     purchase_query = """
    #            SELECT sum(p_o_l.product_qty) AS product_qty, p_o_l.product_id FROM purchase_order_line AS p_o_l
    #            JOIN purchase_order AS p_o ON p_o_l.order_id = p_o.id
    #            INNER JOIN stock_picking_type AS s_p_t ON p_o.picking_type_id = s_p_t.id
    #            WHERE p_o.state IN ('purchase','done')
    #            AND s_p_t.warehouse_id = %s AND p_o_l.product_id in %s group by p_o_l.product_id"""
    #     params = warehouse, product_ids if product_ids else (0, 0)
    #     self._cr.execute(sale_query, params)
    #     sol_query_obj = self._cr.dictfetchall()
    #     self._cr.execute(purchase_query, params)
    #     pol_query_obj = self._cr.dictfetchall()
    #     for obj in categ_products:
    #         sale_value = 0
    #         purchase_value = 0
    #         for sol_product in sol_query_obj:
    #             if sol_product['product_id'] == obj.id:
    #                 sale_value = sol_product['product_uom_qty']
    #         for pol_product in pol_query_obj:
    #             if pol_product['product_id'] == obj.id:
    #                 purchase_value = pol_product['product_qty']
    #         virtual_available = obj.with_context({'warehouse': warehouse}).virtual_available
    #         outgoing_qty = obj.with_context({'warehouse': warehouse}).outgoing_qty
    #         incoming_qty = obj.with_context({'warehouse': warehouse}).incoming_qty
    #         available_qty = virtual_available + outgoing_qty - incoming_qty
    #         value = available_qty * obj.standard_price
    #         vals = {
    #             'sku': obj.default_code,
    #             'name': obj.name,
    #             'category': obj.categ_id.name,
    #             'cost_price': obj.standard_price,
    #             'available': available_qty,
    #             'virtual': virtual_available,
    #             'incoming': incoming_qty,
    #             'outgoing': outgoing_qty,
    #             'net_on_hand': obj.with_context({'warehouse': warehouse}).qty_available,
    #             'total_value': value,
    #             'sale_value': sale_value,
    #             'purchase_value': purchase_value,
    #         }
    #         lines.append(vals)
    #     return lines

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        lines = self.browse(data['ids'])
        employees = lines.employees
        from_date = lines.from_date
        to_date = lines.to_date
        _logger.info('--------------------')
        _logger.info(employees)
        _logger.info(from_date)
        _logger.info(to_date)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Attendance Info')
        red = workbook.add_format({'color': 'red'})
        blue = workbook.add_format({'color': 'blue'})
        cell_format = workbook.add_format({'align': 'center',
                                   'valign': 'vcenter',
                                   'border': 1})
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






                           

        # format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True,'bg_color':'red','valign':'vcenter'})
        # format1 = workbook.add_format({'bg_color':'red'})
        # sheet.set_row(2, 2, format1)
        # sheet.set_row(2, 3, format1)
        # sheet.set_row(2, 4, format1)
        # sheet.set_row(2, 5, format1)
        # sheet.set_row(2, 6, format1)
        # sheet.write(2, 2, 'ساعات التأخر النهائية')
        # sheet.write(2, 3, 'ساعات التأخر')
        # sheet.write(2, 4, 'أيام الخروج بدون اذن')
        # sheet.write(2, 5, 'أيام الغياب')
        # sheet.write(2, 6, 'اسم الموظف')
        # sheet.write(2, 7, 'رقم الهوية')
        # sheet.write(2, 8, 'م')

        # sheet.insert_textbox('C2', """التقرير الشامل - أيام الغياب وساعات العمل
        #                         # من 1442/09/20-2021/05/02 الى 1442/10/19-2021/05/31""",{'object_position': 8})



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
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
