# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


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

    _sql_constraints = [
        (
            'parking_lot_unique',
            'UNIQUE(name)',
            'The parking lot must be unique',
        ),
    ]

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
            if item.price <= 0:
                raise exceptions.ValidationError("The price in field: \"{0}\" must be more than zero!"
                                                 .format(item.vehicle_id.type))

        if not list_check:
            raise exceptions.ValidationError("The type of vehicle is not null!")

