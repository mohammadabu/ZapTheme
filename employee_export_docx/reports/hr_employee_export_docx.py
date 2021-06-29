# -*- coding: utf-8 -*-

from odoo import models, _
from num2words import num2words
from datetime import datetime, date

class SaleOrderExportDocx(models.AbstractModel):
    _name = 'report.hr_export_docx.hr_employee_export_docx'
    _inherit = 'export.docx.abstract'
    _description = 'Hr Employee Export Docx'

    def generate_variables(self, objs):
        # Data for table of sale order line
        user_lang = self.env.user.lang or 'en_US'
        count = 1
        table_line = []
        # for order_line in objs.hr_employee_id.order_line:
        #     table_line.append({
        #         'line_index': str(count),
        #         'product_name': order_line.product_id.name,
        #         'line_description': order_line.name or '',
        #         'product_unit': order_line.product_uom.with_context(lang=user_lang).name,
        #         'product_qty': f'{order_line.product_uom_qty:,.0f}',
        #         'line_unit_price': f'{order_line.price_unit:,.0f}',
        #         'tax_name': ', '.join(order_line.tax_id.mapped('name')) if order_line.tax_id else '',
        #         'line_price_subtotal': f'{order_line.price_subtotal:,.0f}',
        #     })
        #     count += 1
        table_line.append({
                'line_index': "1",
                'product_name': "product_name",
                'line_description': "line_description",
                'product_unit': "product_unit",
                'product_qty': "product_qty",
                'line_unit_price': "line_unit_price",
                'tax_name': '',
                'line_price_subtotal': '',
            })

        # Data for Variable of template
        context = {
            'today': datetime.now().strftime('%d/%m/%Y'),
            'today_date': datetime.now().strftime('%d'),
            'today_month': datetime.now().strftime('%m'),
            'today_year': datetime.now().strftime('%Y'),
            'sale_name': objs.hr_employee_id.name or '',
            'user_name': objs.hr_employee_id.user_id.name if objs.hr_employee_id.user_id else '',
            'partner_name': 'partner_name'  or '',
            'partner_address': 'partner_address',
            'partner_phone':  'partner_phone',
            'partner_email': 'partner_email',
            'partner_vat': 'partner_vat',
            'date_order': 'date_order',
            'validity_date': 'date_order',
            'payment_term':  'date_order',
            'amount_untaxed': 'date_order',
            'amount_tax': '',
            'total_price': '',
            'amount_in_words': "",
            'tbl_contents': table_line,
        }
        return context

    def get_report_name(self, objs):
        timestamp = str(int(datetime.timestamp(datetime.now())))
        report_name = f'{objs.hr_employee_id.id}_{objs.report_template_id.id}_{timestamp}_report.docx'
        return report_name
