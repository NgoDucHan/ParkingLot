# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import timedelta
import math
import datetime


class VehicleType(models.Model):
    _name = "parkinglot.vehicletype"
    _description = "Vehicle Type"
    _rec_name = "type"

    type = fields.Char(string="Vehicle", required=True)

    _sql_constraints = [
        (
            'vehicle_unique',
            'UNIQUE(type)',
            'The type of the vehicle must be unique',
        ),
    ]


class LimitVehiclesInParking(models.Model):
    _name = "parkinglot.limitvehicle"
    _description = "Limit Vehicle"
    _rec_name = "vehicle_id"

    parkinglots_id = fields.Many2one('parkinglot.parkinglots', ondelete='cascade',
                                     string="Limit Vehicle", required=True)

    vehicle_id = fields.Many2one('parkinglot.vehicletype', ondelete='cascade', required=True,
                                 string='Vehicle Reference')
    amount_vehicle = fields.Integer(string="Amount", default=0)

    price_vehicle_on_parkinglot = fields.Float("Price (VND)", required=True, default=2000)

    _sql_constraints = [
        (
            'amount_vehicle_prefix_check',
            'CHECK(amount_vehicle > 0)',
            'The number of the limit vehicle should not be less than zero',
        ),
    ]

    _sql_constraints = [
        (
            'price_vehicle_prefix_check',
            'CHECK(price_vehicle_on_parkinglot > 0)',
            'The number of the limit vehicle should not be less than zero',
        ),
    ]

