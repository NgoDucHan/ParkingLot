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


class ParkingLots(models.Model):
    _name = 'parkinglot.parkinglots'
    _description = 'Parking Lots'

    name = fields.Char(string="Parking Lot Name", required=True)
    location = fields.Char(string="Location", required=True)

    operating_time = fields.Many2one(
        "resource.calendar", string="Operating Time"
    )
    description = fields.Text()

    limit_vehicle_ids = fields.One2many('parkinglot.limitvehicle', 'parkinglots_id',
                                        string='Parking Lots Reference')

    tickets_in_parkinglot_ids = fields.One2many('parkinglot.parkingtickets', 'parkinglots_id',
                                                string='Parking Ticket Reference')

    responsible_id = fields.Many2one('res.users',
                                     ondelete='set null', string="Responsible", index=True)

    parkinglot_sequence_id = fields.Many2one('ir.sequence', string="ParkingLot Sequence", required=True)

    @api.constrains('limit_vehicle_ids')
    def check_unique_vehicle(self):
        type_vehicles = self.limit_vehicle_ids
        for t in type_vehicles:
            if self.env['parkinglot.limitvehicle'].search_count(['&',
                                                                 ('parkinglots_id', '=', t.parkinglots_id.id),
                                                                 ('vehicle_id', '=', t.vehicle_id.id)
                                                                 ]) >= 2:
                raise exceptions.ValidationError("Type of vehicle in Vehicle Reference must be Unique")


class ParkingTickets(models.Model):
    _name = 'parkinglot.parkingtickets'
    _description = 'Parking Tickets'
    _rec_name = 'code_generator'

    start_time = fields.Datetime(default=fields.Datetime.now)
    duration = fields.Integer(help="Duration parking", store=True, compute="_get_all_duration",
                              string="Duration (hours)")
    end_time = fields.Datetime()

    paid = fields.Boolean(default=False, store=True)

    code_generator = fields.Char(default='New')
    # default=lambda self: self.env['ir.sequence'].next_by_code('B5')

    parkinglots_id = fields.Many2one('parkinglot.parkinglots', ondelete='cascade',
                                     string='Parking Lots',
                                     required=True)

    vehicle_type_with_price = fields.Many2one('parkinglot.limitvehicle', ondelete='cascade',
                                              domain="[('parkinglots_id', '=', parkinglots_id)]",
                                              string="Vehicle Type", required=True)

    price_ticket = fields.Float(default=0, compute='_calculate_price', store=True)

    # not start_dt.tzinfo:
    # start_dt = start_dt.replace(tzinfo=utc)

    @api.constrains('start_time')
    def _check_working_time(self):
        calendar = self.parkinglots_id.operating_time
        now = self.start_time.replace(tzinfo=pytz.UTC)
        if not calendar._in_work_time(now):
            raise exceptions.ValidationError("The parking lot is closed!")

        # start_time = self.start_time
        # if not start_time.tzinfo:
        #     start_time = start_time.replace(tzinfo=pytz.UTC)
        #     start_time1 = start_time.replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh"))
        # if self.parkinglots_id.operating_time._get_closest_work_time(start_time):
        #     raise exceptions.ValidationError("{0} \n{1} \n{2} \n{3}".format(start_time, start_time1, self.start_time, self.parkinglots_id.operating_time._get_closest_work_time(start_time)))

    @api.depends('end_time')
    def _calculate_price(self):
        for r in self:
            _price = r.vehicle_type_with_price.price_vehicle_on_parkinglot
            r.price_ticket = _price

    @api.depends('paid')
    def _pay_ticket(self):
        self.price_ticket = self.vehicle_type_with_price.price_vehicle_on_parkinglot

    @api.model
    def create(self, vals):
        parkinglots_id_ref = vals.get('parkinglots_id')
        parkinglots_id = self.env['parkinglot.parkinglots'].browse(parkinglots_id_ref)
        if vals.get('code_generator', _('New')) == _('New'):
            if parkinglots_id.parkinglot_sequence_id:
                vals['code_generator'] = parkinglots_id.parkinglot_sequence_id.next_by_id()
            else:
                vals['code_generator'] = self.env.ref('sequence_parking_lots').next_by_id()
        result = super(ParkingTickets, self).create(vals)
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

    # _sql_constraints = [
    #     (
    #         'date_from_to_check',
    #         'CHECK(start_time < end_time)',
    #         'Start-time must be less than End-time',
    #     ),
    # ]

    @api.constrains('start_time', 'end_time')
    def _check_start_end_time(self):
        if self.end_time:
            if self.start_time > self.end_time:
                raise exceptions.ValidationError("Start-time must be less than End-time")

    @api.onchange('vehicle_type_with_price')
    def _check_amount_vehicle(self):
        if self.vehicle_type_with_price:
            records = self.env['parkinglot.parkingtickets'].search([
                ('vehicle_type_with_price', '=', self.vehicle_type_with_price.vehicle_id.type),
                ('parkinglots_id', '=', self.parkinglots_id.id),
                ('paid', '=', False)
                ])
            if records:
                amount = len(records)
                if amount >= self.vehicle_type_with_price.amount_vehicle:
                    # raise exceptions.ValidationError("Full slots!")
                    return {
                        'warning': {
                            'title': "Full slots",
                            'message': "The amount of slots in parking lot is full "
                                       "(limit: {0} {1}s, current: {2} {1}s)".format(
                                            self.vehicle_type_with_price.amount_vehicle,
                                            self.vehicle_type_with_price.vehicle_id.type,
                                            amount),
                        },
                    }
