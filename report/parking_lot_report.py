# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ParkinglotReport(models.AbstractModel):
    _name = 'report.parking.report_parking_lot'
    _description = 'Parking Lot Report'

    def _get_date(self, start_date=None, end_date=None):
        st_date = fields.Date.from_string(start_date)
        ed_date = fields.Date.from_string(end_date)
        return{
            'start_date': fields.Date.to_string(st_date),
            'end_date': fields.Date.to_string(ed_date),
        }

    def _get_tickets(self, parkinglots, start_date=None, end_date=None):
        parkinglots = self.env['parking.lot'].browse(self.env.context.get('active_ids', []))
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        res = []
        tickets = []
        domain_start_date = ('start_time', '>=', start_date)
        domain_end_date = ('end_time', '<=', end_date)
        for lot in parkinglots:
            tickets += self.env['parking.ticket'].search([
                ('parking_lot_id', '=', lot.id),
                domain_start_date if start_date else ('start_time', '!=', None),
                domain_end_date if end_date else ('end_time', '!=', None)
            ])
        return tickets

    def _get_all_type_vh(self):
        type_vh = self.env['parking.vehicle'].search([('type', '!=', None)])
        return type_vh

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        parking_lot_report = self.env['ir.actions.report']._get_report_from_name('parking.report_parking_lot')
        # parkingtickets = self.env['parking.parkingtickets'].browse(self.ids)
        parkinglots = self.env['parking.lot'].browse(self.env.context.get('active_ids', []))
        return {
            'doc_ids': self.ids,
            'doc_model': parking_lot_report.model,
            'docs': self,
            'parkinglots': parkinglots,
            # 'tickets': parkingtickets,
            'get_date': self._get_date(data['form']['date_from'], data['form']['date_to']),
            'get_tickets': self._get_tickets(
                data['form']['parking_lot_id'],
                data['form']['date_from'],
                data['form']['date_to']
            ),
            'get_type_vh': self._get_all_type_vh(),
        }
