# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from .key_data import SALE_ORDER_KEYS

class KeyTemplate(models.Model):
    _name = "key.template"
    _description = "Keys of Template"


    name = fields.Char(string="Name", required=True, )
    ir_model = fields.Selection(string="Model", selection=[('sale_order', 'Sale Order')],
                                required=True, default='sale_order')
    description = fields.Char(string="Description", required=False, )
    body_html = fields.Html(string="Content", compute='_compute_body_html')
    table_guide_html = fields.Html(string="Table Guide",)

    @api.depends('ir_model')
    def _compute_body_html(self):
        for rec in self:
            if rec.ir_model == 'sale_order':
                data = SALE_ORDER_KEYS
            body_html = '''
                        <table class="table table-hover table-striped">
                              <thead>
                                <tr class="table-primary">
                                  <th scope="col">No.</th>
                                  <th scope="col">Keys</th>
                                  <th scope="col">Description</th>
                                </tr>
                              </thead>
                          <tbody>\n
                        '''
            count = 1
            for row in data:
                body_html += f'''
                        <tr>
                          <th scope="row">{count}</th>
                          <td>{row[0]}</td>
                          <td>{row[1]}</td>
                        </tr>\n
                '''
                count += 1
            body_html += '''
                            </tbody>
                        </table>
                        '''
            rec.body_html = body_html

