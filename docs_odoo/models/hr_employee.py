import time
from datetime import date, datetime,timedelta
from calendar import monthrange
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
import pytz
import json
import io
from odoo import api, fields, models, _
import logging
from docx import Document
from docx.shared import Inches
from odoo.tools import date_utils
from hijri_converter import convert
_logger = logging.getLogger(__name__)
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class HrEmployeeDocuments(models.Model):
    _inherit = 'hr.employee'

    salary_definition = fields.Char()

    job_definition = fields.Char()

    def generate_salary_definition_form(self):
        # return self.env.ref('docs_odoo.sale_order_export_docx').report_action(self)
        return self.pool.get("hr.empaloyee.export.docx.wizard").action_export_docx_report(self)



class SaleOrderExportDocxWizard(models.TransientModel):
    _name = 'hr.empaloyee.export.docx.wizard'
    _description = 'Docx Export Wizard'

    @api.model
    def action_export_docx_report(self):
        return self.env.ref('docs_odoo.sale_order_export_docx').report_action(self)
