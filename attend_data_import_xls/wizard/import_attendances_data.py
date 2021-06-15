from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz


class ImportAttendances(models.TransientModel):

    _name = 'import.attendances'
    _description = "Import Attendances"

    name = fields.Char('File name')
    file = fields.Binary('File')
    state = fields.Selection([('init', 'init'), ('done', 'done')],
                             string='Status', readonly=True, default='init')
    type = fields.Selection([("xlsx", "XLSX")],
                            default="xlsx", string="File type.")
    operation = fields.Selection(
        [('create', 'Create Record'), ('update', 'Update Record')],
        default='create')

    def import_data_through_cron(self):
        self.ensure_one()
        cron_obj = self.env['ir.cron']
        now_time = datetime.now() + timedelta(seconds=2)
        attendances_master = self.env['import.attendances.master'].create({
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
        order_model = self.env['ir.model'].search(
            [('model', '=', 'hr.attendance')])
        cron_data = {
            'name': "Import Attendances" + ' - ' + user_time_zone,
            'code': 'model.import_data(%s)' % attendances_master.id,
            'nextcall': now_time,
            'numbercall': -1,
            'user_id': self._uid,
            'model_id': order_model.id,
            'state': 'code',
        }

        cron = cron_obj.sudo().create(cron_data)
        attendances_master.cron_id = cron.id
        self.state = 'done'
        return {
            'name': _('Import Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'import.attendances',
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
