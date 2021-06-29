# -*- coding: utf-8 -*-
{
    'name': "Employee Export Docx Old",
    'summary': "Module To Export Docx File",
    'description': """
        This module will help you to export sale order records to docx file.
    """,
    'author': 'We can Odoo it',
    'sequence': 270,
    'website': "",
    'category': 'Reporting',
    'version': '0.1',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'docxtpl',
        ],
    },
    'depends': [
        'base',
        'web',
        'hr',
    ],
    'data': [
        'data/key_template_data.xml',
        'data/hr_employee_report_data.xml',
        'security/ir.model.access.csv',

        'views/webclient_templates.xml',
        'views/key_template.xml',
        'views/ir_attachment.xml',
        'wizards/hr_employee_export_docx_wizard.xml',
        'views/hr_employee_view.xml',

        'menu/menu.xml',
    ],
    'demo': [
        # 'demo/report.xml',
    ],
    'installable': True,
    'application': True,
    'active': True,
}
