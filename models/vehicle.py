# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import timedelta
import math
import datetime


class Vehicle(models.Model):
    _name = "parking.vehicle"
    _description = "Vehicle"
    _rec_name = "type"

    type = fields.Char(string="Vehicle", required=True)

    _sql_constraints = [
        (
            'vehicle_unique',
            'UNIQUE(type)',
            'The type of the vehicle must be unique',
        ),
    ]


class PriceList(models.Model):
    _name = "parking.pricelist"
    _description = "Price List"
    _rec_name = "vehicle_id"

    parking_lot_id = fields.Many2one('parking.lot', ondelete='cascade',
                                     string="Parking Lot Reference", required=True)

    vehicle_id = fields.Many2one('parking.vehicle', ondelete='cascade', required=True,
                                 string='Vehicle Reference')
    amount_vehicle = fields.Integer(string="Amount", default=0)

    price = fields.Float("Price (VND)", required=True, default=2000)

    _sql_constraints = [
        (
            'amount_vehicle_prefix_check',
            'CHECK(amount_vehicle > 0)',
            'The number of the limit vehicle should not be less than zero',
        ),
    ]

