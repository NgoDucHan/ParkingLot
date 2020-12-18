# -*- coding: utf-8 -*-

import pytz
import math

from odoo import models, fields, api, exceptions, _


class ParkingTicket(models.Model):
    _name = 'parking.ticket'
    _description = 'Parking Ticket'
    _rec_name = 'code_generator'

    start_time = fields.Datetime(default=fields.Datetime.now)
    duration = fields.Integer(help="Duration parking", store=True, compute="_compute_get_all_duration",
                              string="Duration (hours)")
    end_time = fields.Datetime()

    paid = fields.Boolean(default=False, store=True)

    code_generator = fields.Char(default='New')
    # default=lambda self: self.env['ir.sequence'].next_by_code('B5')

    parking_lot_id = fields.Many2one('parking.lot', ondelete='cascade',
                                    string='Parking Lot',
                                    required=True)

    pricelist_id = fields.Many2one('parking.pricelist', ondelete='cascade',
                                   domain="[('parking_lot_id', '=', parking_lot_id)]",
                                   string="Price List", required=True)

    price_ticket = fields.Float(default=0, compute='_compute_calculate_price', store=True)

    @api.constrains('start_time')
    def _check_working_time(self):
        calendar = self.parking_lot_id.calendar_id
        now = self.start_time.replace(tzinfo=pytz.UTC)
        if not calendar._in_work_time(now):
            raise exceptions.ValidationError("The parking lot is closed!")

    @api.depends('end_time')
    def _compute_calculate_price(self):
        for r in self:
            _price = r.pricelist_id.price
            r.price_ticket = _price

    @api.depends('paid')
    def ticket_price(self):
        self.price_ticket = self.pricelist_id.price

    @api.model
    def create(self, vals):
        parking_lot_id_ref = vals.get('parking_lot_id')
        parking_lot_id = self.env['parking.lot'].browse(parking_lot_id_ref)
        if vals.get('code_generator', _('New')) == _('New'):
            if parking_lot_id.sequence_id:
                vals['code_generator'] = parking_lot_id.sequence_id.next_by_id()
            else:
                vals['code_generator'] = self.env.ref('sequence_parking_lot').next_by_id()
        result = super(ParkingTicket, self).create(vals)
        return result

    @api.model
    def update_all_duration(self):
        records = self.search([('paid', '=', False)])
        records.get_duration()

    def get_duration(self):
        records = self
        for r in records:
            r.end_time = fields.Datetime.now()
            if r.start_time:
                delta = r.end_time - r.start_time
                n = delta.total_seconds() / 60 / 60
                r.duration = int(math.floor(n + 0.5))

    @api.onchange('start_time', 'end_time')
    @api.depends('start_time', 'end_time')
    def _compute_get_all_duration(self):
        self.get_duration()

    @api.constrains('start_time', 'end_time')
    def _check_start_end_time(self):
        if self.end_time:
            if self.start_time > self.end_time:
                raise exceptions.ValidationError("Start-time must be less than End-time")

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        if self.pricelist_id:
            type_name = self.pricelist_id.vehicle_id.type
            records = self.env['parking.ticket'].search([
                ('pricelist_id', '=', type_name),
                ('parking_lot_id', '=', self.parking_lot_id.id),
                ('paid', '=', False)
            ])
            if records:
                amount = len(records)
                amount_default = self.pricelist_id.amount_vehicle
                if amount >= amount_default:
                    # raise exceptions.ValidationError("Full slots!")
                    return {
                        'warning': {
                            'title': "Warning: Full slots",
                            'message': "The amount of slots in parking lot is full "
                                       "(limit: {0} {1}s, current: {2} {1}s)".format(
                                        amount_default,
                                        type_name,
                                        amount),
                        },
                    }

    # @api.onchange('pricelist_id')
    # def _check_amount_vehicle(self):
    #     if self.pricelist_id:
    #         amount_vehicle = self.env['parking.ticket'].search_count([
    #             ('pricelist_id', '=', self.pricelist_id.vehicle_id.type),
    #             ('parking_lot_id', '=', self.parking_lot_id.id),
    #             ('paid', '=', False)
    #         ])
    #         if amount_vehicle:
    #             if amount_vehicle >= self.pricelist_id.amount_vehicle:
    #                 raise exceptions.ValidationError("Full slots!")