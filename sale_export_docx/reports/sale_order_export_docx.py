# -*- coding: utf-8 -*-

from odoo import models, _
from num2words import num2words
from datetime import datetime, date

class SaleOrderExportDocx(models.AbstractModel):
    _name = 'report.sale_export_docx.sale_order_export_docx'
    _inherit = 'export.docx.abstract'
    _description = 'Sale Order Export Docx'

    def generate_variables(self, objs):
        # Data for table of sale order line
        user_lang = self.env.user.lang or 'en_US'
        count = 1
        table_line = []
        for order_line in objs.sale_order_id.order_line:
            table_line.append({
                'line_index': str(count),
                'product_name': order_line.product_id.name,
                'line_description': order_line.name or '',
                'product_unit': order_line.product_uom.with_context(lang=user_lang).name,
                'product_qty': f'{order_line.product_uom_qty:,.0f}',
                'line_unit_price': f'{order_line.price_unit:,.0f}',
                'tax_name': ', '.join(order_line.tax_id.mapped('name')) if order_line.tax_id else '',
                'line_price_subtotal': f'{order_line.price_subtotal:,.0f}',
            })
            count += 1

        # Data for Variable of template
        context = {
            'today': datetime.now().strftime('%d/%m/%Y'),
            'today_date': datetime.now().strftime('%d'),
            'today_month': datetime.now().strftime('%m'),
            'today_year': datetime.now().strftime('%Y'),
            'sale_name': objs.sale_order_id.name or '',
            'user_name': objs.sale_order_id.user_id.name if objs.sale_order_id.user_id else '',
            'partner_name': objs.sale_order_id.partner_id.name  or '',
            'partner_address': self.get_partner_address(objs.sale_order_id.partner_id),
            'partner_phone': objs.sale_order_id.partner_id.phone or '',
            'partner_email': objs.sale_order_id.partner_id.email or '',
            'partner_vat': objs.sale_order_id.partner_id.vat or '',
            'date_order': objs.sale_order_id.date_order.strftime('%d/%m/%Y') if objs.sale_order_id.date_order else '',
            'validity_date': objs.sale_order_id.validity_date.strftime('%d/%m/%Y') if objs.sale_order_id.validity_date else '',
            'payment_term': objs.sale_order_id.payment_term_id.name if objs.sale_order_id.payment_term_id else '',
            'amount_untaxed': f'{objs.sale_order_id.amount_untaxed:,.0f} {objs.sale_order_id.currency_id.symbol}',
            'amount_tax': f'{objs.sale_order_id.amount_tax:,.0f} {objs.sale_order_id.currency_id.symbol}',
            'total_price': f'{objs.sale_order_id.amount_total:,.0f} {objs.sale_order_id.currency_id.symbol}',
            'amount_in_words': f"{num2words(round(objs.sale_order_id.amount_total), lang=user_lang).capitalize()}"
                               f" {objs.sale_order_id.currency_id.name}.",
            'tbl_contents': table_line,
        }
        return context

    def get_report_name(self, objs):
        timestamp = str(int(datetime.timestamp(datetime.now())))
        report_name = f'{objs.sale_order_id.id}_{objs.report_template_id.id}_{timestamp}_report.docx'
        return report_name
