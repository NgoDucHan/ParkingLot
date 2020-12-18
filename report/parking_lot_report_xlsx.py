# -*- coding: utf-8 -*-

from odoo import models


class ParkingLotReportXlsx(models.AbstractModel):
    _name = 'report.parking.report_parking_lot_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, parking_lot):
        format1 = workbook.add_format({'border': 1, 'align': 'vcenter'})
        format2 = workbook.add_format({'border': 1})

        def cal_price(type, parking_lot_id):
            ticks = self.env['parking.ticket'].search([('parking_lot_id', '=', parking_lot_id.id)])
            total = 0
            count = 0
            for tick in ticks:
                if tick.pricelist_id.vehicle_id.type == type and tick.paid is True:
                    total += tick.price_ticket
                    count += 1
            return count, total

        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        sheet = workbook.add_worksheet("Report Parking Lot xlsx")

        sheet.merge_range(4, 2, 6, 3, 'Parking Lot', merge_format1)

        vehicles = self.env['parking.vehicle'].search([])

        a1 = 5; a2 = 4; b1 = 5; b2 = 5
        i = 0

        for vh in vehicles:
            sheet.merge_range(a1, a2 + 2 * i, b1, b2 + 2 * i, vh.type, merge_format1)

            sheet.write(a1 + 1, a2 + 2 * i, "Amount", format1)

            sheet.set_column(b2 + 2 * i, b2 + 2 * i, 10)
            sheet.write(b1 + 1, b2 + 2 * i, "Total Price", format1)

            i += 1

        sheet.merge_range(a1 - 1, a2, b1 - 1, b2 + 2 * (i - 1), "Type", merge_format1)
        sheet.merge_range(a1 - 1, a2 + 2 * i, b1, b2 + 2 * i, "Summary", merge_format1)
        sheet.write(a1 + 1, a2 + 2 * i, "Amount", format1)

        sheet.set_column(b2 + 2 * i, b2 + 2 * i, 10)
        sheet.write(b1 + 1, b2 + 2 * i, "Total Price", format1)

        x1 = 7; x2 = 2; y1 = 7; y2 = 3
        i = 1
        j = 0


        for pk in parking_lot:
            sheet.merge_range(x1 + j, x2, y1 + j, y2, pk.name, merge_format1)
            amount = 0; total_price = 0
            for vh in vehicles:
                result = cal_price(vh.type, pk)
                amount += result[0]
                total_price += result[1]
                sheet.write(x1 + j, x2 + 2 * i, result[0], format2)
                sheet.write(y1 + j, y2 + 2 * i, result[1], format2)
                i += 1
            sheet.write(x1 + j, x2 + 2 * i, amount, format2)
            sheet.write(y1 + j, y2 + 2 * i, total_price, format2)
            i = 1
            j += 1