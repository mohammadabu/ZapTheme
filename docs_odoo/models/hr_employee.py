import time
from datetime import date, datetime,timedelta
from calendar import monthrange
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
import pytz
import json
import io
from odoo import api, fields, models, _
import logging
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
        self.pool.get("wizard.hr.employee.history.docs").generate_salary_definition_form(self)




class StockReport(models.TransientModel):
    _name = "wizard.hr.employee.history.docs"
    _description = "Current Docs History"


    @api.model
    def generate_salary_definition_form(self):
        data = {
            'ids': self.ids,
            'model': self._name
        }
        return {
            'type': 'ir_actions_docs_download',
            'data': {'model': 'wizard.hr.employee.history.docs',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'docx',
                     'report_name': 'التقرير الشامل لأيام الغياب وساعات العمل',
                    }
        }    

    def get_docs_report(self, data, response):
        output = io.BytesIO()
        # lines = self.browse(data['ids'])
        # workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        _logger.info('test test tes n3 n32 n32')
        # workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()    