from odoo import models, fields, api, exceptions
import datetime

class ReportParkingLotWizard(models.TransientModel):
    # sau 24h cac record cua model nay se bi xoa
    # vi du lieu nay khong su dung voi muc dich luu tru
    _name = "parkinglot.report.wizard"
    _description = "Create Report By Condition!"

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    parkinglots_id = fields.Many2one('parkinglot.parkinglots', string='Parking Lots')

    @api.constrains('date_from', 'date_to')
    def check_date_from_to(self):
        date_from = self.date_from
        date_to = self.date_to
        if date_from:
            if date_from > datetime.date.today():
                raise exceptions.ValidationError('Date-from must be less than or equal today!')
            if date_to:
                if date_from > date_to:
                    raise exceptions.ValidationError('Date-from must be less than date-to!')

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['parkinglots_id'] = self.env.context.get('active_ids', [])
        parkinglots = self.env['parkinglot.parkinglots'].browse(data['parkinglots_id'])

        datas = {
            'ids': [],
            'model': 'parkinglot.parkinglots',
            'form': data
        }

        return self.env.ref("parkinglot.action_report_parkinglot").report_action(parkinglots, data=datas)
