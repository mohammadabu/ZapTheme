# -*- coding: utf-8 -*-

from sys import platform
from subprocess import Popen
from docx2pdf import convert
from datetime import datetime, date
import os
import base64
import logging
from odoo import models, tools
from odoo.addons.sale_export_docx.reports import template
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import docx
_logger = logging.getLogger(__name__)

try:
    from docxtpl import DocxTemplate
except ImportError:
    _logger.debug('Can not import DocxTemplate')


class ExportDocxAbstract(models.AbstractModel):
    _name = 'export.docx.abstract'
    _description = 'Export Docx Abstract Model'

    def _get_objs_for_report(self, docids, data):
        if docids:
            ids = docids
        elif data and 'context' in data:
            ids = data["context"].get('active_ids', [])
        else:
            ids = self.env.context.get('active_ids', [])
        return self.env[self.env.context.get('active_model')].browse(ids)

    def create_docx_report(self, docids, data):
        objs = self._get_objs_for_report(docids, data)
        return self.generate_docx_report( data, objs), 'docx'

    def generate_docx_report(self, data, objs):
        timestamp = str(int(datetime.timestamp(datetime.now())))
        path_docx = '/var/lib/odoo/.local/share/Odoo/'

        document = Document()
        paragraph = document.add_paragraph('Python is cool')
        paragraph.style = document.styles.add_style('', WD_STYLE_TYPE.PARAGRAPH)
        font = paragraph.style.font
        font.name = 'Times New Roman'



        path_docx = path_docx + '/EmployeeDocx_' + timestamp + ".docx"
        document.save(path_docx)


        
        report_doxc_path = path_docx
        with open(report_doxc_path, mode='rb') as file:
            fileContent = file.read()

        try:
            os.remove(report_doxc_path)
        except Exception as e:
            _logger.warning(repr(e))

        return fileContent

    def generate_variables(self, objs):
        raise NotImplementedError()

    def get_report_name(self, objs):
        raise NotImplementedError()

    def _save_file(self, template_path, data):
        out_stream = open(template_path, 'wb')
        try:
            out_stream.write(data)
        finally:
            out_stream.close()

    def get_partner_address(self, obj=None):
        if not obj:
            return ''
        address = ''
        address += f'{obj.street}' if obj.street else ''
        address += f', {obj.street}' if obj.street2 else ''
        address += f', {obj.city}' if obj.city else ''
        address += f', {obj.state_id.name}' if obj.state_id else ''
        address += f', {obj.country_id.name}' if obj.country_id else ''
        return address
