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


class AttendanceReportExcel(models.TransientModel):
    _name = "wizard.attendance.history.docx"
    _description = "Current Attendance History in Docx"

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name
        }
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'wizard.attendance.history.excel',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'docx',
                     'report_name': 'التقرير الشامل لأيام الغياب وساعات العمل',
                    }
        }
    
    
    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        lines = self.browse(data['ids'])
        # workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
