{
    'name': 'Attend Data Import - XLS',
    'version': '13.0.0.1.0',
    'depends': ["hr_attendance"],
    'data': [
        'wizard/import_attendances_data_view.xml',
        'views/import_attendances_history_view.xml',
        'views/import_attendances_master_view.xml',
        'security/ir.model.access.csv',
        # 'data/data.xml',
    ],
}
