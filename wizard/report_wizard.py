from odoo import models, fields, api


class ReportParkingLotWizard(models.TransientModel):
    # sau 24h cac record cua model nay se bi xoa
    # vi du lieu nay khong su dung voi muc dich luu tru
    _name = "parking.report.wizard"
    _description = "Create Report By Condition!"

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    parking_lot_id = fields.Many2one('parking.lot', string='Parking Lot')

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['parking_lot_id'] = self.env.context.get('active_ids', [])
        parkinglots = self.env['parking.lot'].browse(data['parking_lot_id'])

        datas = {
            'ids': [],
            'model': 'parking.lot',
            'form': data
        }

        return self.env.ref("parking.action_report_parking_lot").report_action(parkinglots, data=datas)
