
import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ParkinglotReport(models.AbstractModel):
    _name = 'report.parkinglot.report_parkinglots'
    _description = 'Parking Lot Report'

    def _get_date(self, start_date=None, end_date=None):
        st_date = fields.Date.from_string(start_date)
        ed_date = fields.Date.from_string(end_date)
        return{
            'start_date': fields.Date.to_string(st_date),
            'end_date': fields.Date.to_string(ed_date),
        }

    def _get_tickets(self, parkinglots, start_date=None, end_date=None):
        parkinglots = self.env['parkinglot.parkinglots'].browse(self.env.context.get('active_ids', []))
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        res = []
        tickets = []
        domain_start_date = ('start_time', '>=', start_date)
        domain_end_date = ('end_time', '<=', end_date)
        for lot in parkinglots:
            tickets += self.env['parkinglot.parkingtickets'].search([
                ('parkinglots_id', '=', lot.id),
                domain_start_date if start_date else ('start_time', '!=', None),
                domain_end_date if end_date else ('end_time', '!=', None)
            ])
        return tickets

    def _get_all_type_vh(self):
        type_vh = self.env['parkinglot.vehicletype'].search([('type', '!=', None)])
        return type_vh

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        parkinglot_report = self.env['ir.actions.report']._get_report_from_name('parkinglot.report_parkinglots')
        # parkingtickets = self.env['parkinglot.parkingtickets'].browse(self.ids)
        parkinglots = self.env['parkinglot.parkinglots'].browse(self.env.context.get('active_ids', []))
        return {
            'doc_ids': self.ids,
            'doc_model': parkinglot_report.model,
            'docs': self,
            'parkinglots': parkinglots,
            # 'tickets': parkingtickets,
            'get_date': self._get_date(data['form']['date_from'], data['form']['date_to']),
            'get_tickets': self._get_tickets(
                data['form']['parkinglots_id'],
                data['form']['date_from'],
                data['form']['date_to']
            ),
            'get_type_vh': self._get_all_type_vh(),
        }
