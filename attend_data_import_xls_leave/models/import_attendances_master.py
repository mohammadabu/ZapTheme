from odoo import models, fields


class ImportAttendancesMaster(models.Model):

    _name = 'import.attendances.master'
    _description = "Import Attendances Status"
    _rec_name = 'file'

    file = fields.Binary('File')
    filename = fields.Char('File Name')
    user_id = fields.Many2one("res.users", "Imported by")
    cron_id = fields.Many2one('ir.cron', "Running Cron")
    file_updated = fields.Boolean("File Updated?")
    status = fields.Selection([('in_process', 'In Progress'),
                               ("imported", "Imported"), ("failed", "Failed")],
                              default='in_process')
    type = fields.Selection([("csv", "CSV"), ("xlsx", "XLSX")],
                            default="csv", string="File type.")
    operation = fields.Selection(
        [('create', 'Create Record'), ('update', 'Update Record')],
        default='create')
