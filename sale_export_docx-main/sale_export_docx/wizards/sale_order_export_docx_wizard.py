# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderExportDocxWizard(models.TransientModel):
    _name = 'sale.order.export.docx.wizard'
    _description = 'Docx Export Wizard'

    def _default_template_id(self):
        template_id = self.env['ir.attachment'].search([('res_model', '=', 'sale.order'), ('public', '=', True),
                                                        ('access_token', '=', 'sale.order')], limit=1)
        return template_id

    report_template_id = fields.Many2one(comodel_name="ir.attachment", string="Template", default=_default_template_id,
                                         required=True)

    sale_order_id = fields.Many2one('sale.order', string='Report Object',
                                    default=lambda self: self.env.context.get('active_id'))

    def action_export_docx_report(self):
        return self.env.ref('sale_export_docx.sale_order_export_docx').report_action(self)

