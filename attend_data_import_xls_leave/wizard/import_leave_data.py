from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz


class ImportLeave(models.TransientModel):

    _name = 'import.leave'
    _description = "Import Leave"

    name = fields.Char('File name')
    file = fields.Binary('File')
    state = fields.Selection([('init', 'init'), ('done', 'done')],
                             string='Status', readonly=True, default='init')
    type = fields.Selection([("xlsx", "XLSX")],
                            default="xlsx", string="File type.")
    operation = fields.Selection(
        [('create', 'Create Record'), ('update', 'Update Record')],
        default='create')

    def import_data_through_cron_leave(self):
        self.ensure_one()
        cron_obj = self.env['ir.cron']
        now_time = datetime.now() + timedelta(seconds=1)
        leave_master = self.env['import.leave.master'].create({
            'file': self.file,
            'filename': self.name,
            'type': self.type,
            'file_updated': True,
            'user_id': self._uid,
            'status': 'in_process',
            'operation': self.operation,
        })

        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        user_time_zone = datetime.strftime(pytz.utc.localize(
            datetime.strptime(datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S'),
                              DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),
            DEFAULT_SERVER_DATETIME_FORMAT)
        self.state = 'done'
        self.pool.get("hr.leave").import_data(self,leave_master.id)
        return {
            'name': _('Import Leave'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'import.leave',
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
