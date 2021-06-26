# -*- coding: utf-8 -*-
{
    'name': "Sale Export Docx",
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
        'sale_management',
    ],
    'data': [
        'data/key_template_data.xml',
        'data/sale_order_report_data.xml',
        'security/ir.model.access.csv',

        'views/webclient_templates.xml',
        'views/key_template.xml',
        'views/ir_attachment.xml',
        'wizards/sale_order_export_docx_wizard.xml',
        'views/sale_order_view.xml',

        'menu/menu.xml',
    ],
    'demo': [
        # 'demo/report.xml',
    ],
    'installable': True,
    'application': True,
    'active': True,
}
