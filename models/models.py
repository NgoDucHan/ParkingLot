# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import timedelta
import math
import datetime
import pytz
from pytz import timezone, UTC
from dateutil.relativedelta import relativedelta
from odoo.osv import expression


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _in_work_time(self, dt, resource=None):
        """Return the boolean work interval boundary within the search range.
            if the dt in the range -> return True, else False.
        :param dt: reference datetime
        :rtype: datetime | None
        """

        if resource is None:
            resource = self.env['resource.resource']

        assert dt.tzinfo, 'Provided datetimes needs to be timezoned'
        dt = dt.astimezone(timezone(self.tz))

        range_start = dt + relativedelta(hour=0, minute=0, second=0)
        range_end = dt + relativedelta(days=1, hour=0, minute=0, second=0)

        for interval in self._work_intervals_batch(range_start, range_end, resource)[resource.id]:
            if interval[0] <= dt <= interval[1]:
                return True
        return False


class ParkingLot(models.Model):
    _name = 'parking.lot'
    _description = 'Parking Lot'

    name = fields.Char(string="Parking Lot Name", required=True)
    location = fields.Char(string="Location", required=True)

    calendar_id = fields.Many2one(
        "resource.calendar", string="Operating Time"
    )
    description = fields.Text()

    pricelist_ids = fields.One2many('parking.pricelist', 'parking_lot_id',
                                    string='Parking Lot Reference')

    ticket_ids = fields.One2many('parking.ticket', 'parking_lot_id',
                                 string='Parking Ticket Reference')

    responsible_id = fields.Many2one('res.users',
                                     ondelete='set null', string="Responsible", index=True)

    sequence_id = fields.Many2one('ir.sequence', string="Parking Lot Sequence", required=True)

    def show_tickets(self):
        id = self.id
        domain = [('parking_lot_id', '=', id)]
        view_id_tree = self.env['ir.ui.view'].search([('name', '=', "parking.ticket.tree")])

        return {
            'type': 'ir.actions.act_window',
            'name': _('Tickets'),
            'res_model': 'parking.ticket',
            'view_mode': 'tree,form',
            'views': [(view_id_tree[0].id, 'tree'), (False, 'form')],
            'context': {'search_default_is_paid': 1},
            'target': 'current',
            'domain': domain,
        }

    @api.constrains('pricelist_ids')
    def _check_vehicle_unique_time(self):
        list_check = self.pricelist_ids
        for item in list_check:
            if self.env['parking.pricelist'].search_count(['&', ('parking_lot_id', '=', item.parking_lot_id.id),
                                                                ('vehicle_id', '=', item.vehicle_id.id)]) >= 2:
                raise exceptions.ValidationError("The type of the vehicle in Vehicle Reference must be unique")


class ParkingTicket(models.Model):
    _name = 'parking.ticket'
    _description = 'Parking Ticket'
    _rec_name = 'code_generator'

    start_time = fields.Datetime(default=fields.Datetime.now)
    duration = fields.Integer(help="Duration parking", store=True, compute="_get_all_duration",
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

    price_ticket = fields.Float(default=0, compute='_calculate_price', store=True)

    @api.constrains('start_time')
    def _check_working_time(self):
        calendar = self.parking_lot_id.calendar_id
        now = self.start_time.replace(tzinfo=pytz.UTC)
        if not calendar._in_work_time(now):
            raise exceptions.ValidationError("The parking lot is closed!")

    @api.depends('end_time')
    def _calculate_price(self):
        for r in self:
            _price = r.pricelist_id.price
            r.price_ticket = _price

    @api.depends('paid')
    def _pay_ticket(self):
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
    def _update_all_duration(self):
        records = self.search([('paid', '=', False)])
        records._get_duration()

    def _get_duration(self):
        for r in self:
            r.end_time = fields.Datetime.now()
            if r.start_time:
                delta = r.end_time - r.start_time
                n = delta.total_seconds() / 60 / 60
                r.duration = int(math.floor(n + 0.5))

    @api.onchange('start_time', 'end_time')
    @api.depends('start_time', 'end_time')
    def _get_all_duration(self):
        self._get_duration()

    @api.constrains('start_time', 'end_time')
    def _check_start_end_time(self):
        if self.end_time:
            if self.start_time > self.end_time:
                raise exceptions.ValidationError("Start-time must be less than End-time")

    @api.onchange('pricelist_id')
    def _check_amount_vehicle(self):
        if self.pricelist_id:
            records = self.env['parking.ticket'].search([
                ('pricelist_id', '=', self.pricelist_id.vehicle_id.type),
                ('parking_lot_id', '=', self.parking_lot_id.id),
                ('paid', '=', False)
            ])
            if records:
                amount = len(records)
                if amount >= self.pricelist_id.amount_vehicle:
                    # raise exceptions.ValidationError("Full slots!")
                    return {
                        'warning': {
                            'title': "Full slots",
                            'message': "The amount of slots in parking lot is full "
                                       "(limit: {0} {1}s, current: {2} {1}s)".format(
                                        self.pricelist_id.amount_vehicle,
                                        self.pricelist_id.vehicle_id.type,
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