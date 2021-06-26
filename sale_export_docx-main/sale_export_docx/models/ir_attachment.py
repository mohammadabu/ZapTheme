# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    active = fields.Boolean('Active', default=True)

    @api.constrains('name')
    def _check_datas(self):
        for rec in self:
            file_name = rec.name.lower()
            if rec.res_model in ['sale.order'] and rec.res_model == rec.access_token \
                    and not any(file_name.endswith(extention) for extention in ['.docx', '.doc',]):
                raise ValidationError(_('You can only attach MS Word file!'))