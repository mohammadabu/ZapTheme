# -*- coding: utf-8 -*-

from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, route, request
from odoo.tools.safe_eval import safe_eval
import werkzeug

import json
import time


class ReportController(report.ReportController):
    @route([
        '/report/<converter>/<reportname>',
        '/report/<converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report = request.env['ir.actions.report']._get_report_from_name(reportname)
        context = dict(request.env.context)
        if docids:
            docids = [int(i) for i in docids.split(',')]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the one
            # from the webclient *but* if the user explicitely wants to
            # change the lang, this mechanism overwrites it.
            data['context'] = json.loads(data['context'])
            if data['context'].get('lang'):
                del data['context']['lang']
            context.update(data['context'])
        if converter == 'html':
            html = report.with_context(context).render_qweb_html(docids, data=data)[0]
            return request.make_response(html)
        elif converter == 'pdf':
            # Get filename for report
            filepart = "report"

            if docids:
                if len(docids) > 1:
                    filepart = "%s (x%s)" % (
                    request.env['ir.model'].sudo().search([('model', '=', report.model)]).name, str(len(docids)))
                elif len(docids) == 1:
                    obj = request.env[report.model].browse(docids)
                    if report.print_report_name:
                        filepart = safe_eval(report.print_report_name, {'object': obj, 'time': time})
            pdf = report.with_context(context).render_qweb_pdf(docids, data=data)[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
                              ('Content-Disposition', 'filename="%s.pdf"' % filepart.encode('utf-8'))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        if converter == 'text':
            text = report.with_context(context).render_qweb_text(docids, data=data)[0]
            texthttpheaders = [('Content-Type', 'text/plain'), ('Content-Length', len(text))]
            return request.make_response(text, headers=texthttpheaders)
        elif converter == 'docx':
            docx = report.with_context(context).render_docx(
                docids, data=data
            )[0]
            file_name = "export_as_docx"
            if docids:
                if len(docids) > 1:
                    file_name = "%s (x%s)" % (
                    request.env['ir.model'].sudo().search([('model', '=', report.model)]).name, str(len(docids)))
                elif len(docids) == 1:
                    if report.print_report_name:
                        file_name = report.print_report_name

            docxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
                ('Content-Length', len(docx)),
                ('Content-Disposition', content_disposition(file_name + '.docx'))]
            return request.make_response(docx, headers=docxhttpheaders)
        else:
            raise werkzeug.exceptions.HTTPException(description='Converter %s not implemented.' % converter)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )

