{

    'name': 'Password Security',
    "summary": "Allow admin to set password security requirements.",
    'version': '13.0',
    'author':
        "LasLabs, "
        "Kaushal Prajapati, "
        "Tecnativa, "
        "initOS GmbH, "
        "Boraq-Group, "
        "Odoo Community Association (OCA)",
    'category': 'Base',
    'depends': [
        'auth_signup',
        'auth_password_policy_signup',
    ],
    'external_dependencies': {
        'python': ['zxcvbn'],
    },
    "website": "https://github.com/OCA/server-auth",
    "license": "LGPL-3",
    "images": ['static/description/cover.png'],
    "data": [
        'views/password_security.xml',
        'views/res_company_view.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
        'security/res_users_pass_history.xml',
    ],
    "demo": [
        'demo/res_users.xml',
    ],
    'installable': True,
}
