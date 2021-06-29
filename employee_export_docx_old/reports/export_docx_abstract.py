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

_logger = logging.getLogger(__name__)

try:
    from docxtpl import DocxTemplate
except ImportError:
    _logger.debug('Can not import DocxTemplate')


class ExportDocxAbstract(models.AbstractModel):
    _name = 'export.docx.abstract'
    _description = 'Export Docx Abstract Model'

    def _get_objs_for_report(self, docids, data):
        """
        Returns objects for xlx report.  From WebUI these
        are either as docids taken from context.active_ids or
        in the case of wizard are in data.  Manual calls may rely
        on regular context, setting docids, or setting data.

        :param docids: list of integers, typically provided by
            qwebactionmanager for regular Models.
        :param data: dictionary of data, if present typically provided
            by qwebactionmanager for TransientModels.
        :param ids: list of integers, provided by overrides.
        :return: recordset of active model for ids.
        """
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
        template_folder_path = tools.config.get('data_dir', os.path.dirname(template.__file__))
        docx_template_name = f'template_{objs.report_template_id.id}_{timestamp}'
        report_name = self.get_report_name(objs)

        template_path = os.path.join(template_folder_path, docx_template_name)
        report_doxc_path = os.path.join(template_folder_path, report_name)

        # Function to create docx template
        self._save_file(
            template_path, base64.b64decode(objs.report_template_id.datas))

        # Open a document base on template
        document = DocxTemplate(template_path)

        # Define variables
        context = self.generate_variables(objs)

        # Render data to template
        document.render(context)

        # Save Report as docx file
        document.save(report_doxc_path)

        # Read Docx report by binary
        with open(report_doxc_path, mode='rb') as file:
            fileContent = file.read()

        # Delete docx template
        try:
            os.remove(template_path)
        except Exception as e:
            _logger.warning(repr(e))

        # Delete docx report
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
