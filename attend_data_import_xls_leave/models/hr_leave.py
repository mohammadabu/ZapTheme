# -*- coding: utf-8 -*-
from odoo import api, models, fields, exceptions, _
import logging
import base64
from xlrd import open_workbook
_logger = logging.getLogger(__name__)
class ImportHrLeave(models.Model):
    _inherit = 'hr.leave'        
    def import_data(self, part_master_id=False):
        datafile = part_master.file
        temp_path = tempfile.gettempdir()
        file_data = base64.decodestring(datafile)
        fp = open(temp_path + '/xsl_file.xls', 'wb+')
        fp.write(file_data)
        fp.close()
        wb = open_workbook(temp_path + '/xsl_file.xls')