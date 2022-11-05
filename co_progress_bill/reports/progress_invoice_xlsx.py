from odoo.http import request
from odoo import models, api, fields
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta


class VendBillReportXls(models.AbstractModel):
    _name = 'report.co_progress_bill.progress_invoice_xlsx_template'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, invoices):
        table_header = self.table_header_format(workbook)
        table_header2 = self.table_header_format2(workbook)
        table_content = self.table_content_format(workbook)
        date_format_bold = workbook.add_format({
            'num_format': 'YYYY-MM-DD',
            'bold': True,
            'align': 'center',
            'font_color': 'blue',
        })
        for inv in invoices:
            if inv.number:
                worksheet = workbook.add_worksheet(inv.number)
            else:
                worksheet = workbook.add_worksheet("Progress Invoice")
            worksheet.right_to_left()
            worksheet.set_column(0, 2, 15)
            worksheet.set_column(3, 5, 10)
            worksheet.set_column(2, 7, 20)
            worksheet.merge_range(0, 0, 2, 7, "مستخلص عملاء رقم: {}".format(inv.number), self.header_format(workbook))
            worksheet.merge_range(4, 0, 4, 1, "العميل", table_header2)
            worksheet.merge_range(5, 0, 5, 1, inv.partner_id.name, table_content)
            worksheet.merge_range(4, 3, 4, 4, "من تاريخ", table_header2)
            worksheet.merge_range(5, 3, 5, 4, inv.date_from, date_format_bold)
            worksheet.merge_range(4, 6, 4, 7, "الي تاريخ", table_header2)
            worksheet.merge_range(5, 6, 5, 7, inv.date_to, date_format_bold)
            ########################################################
            worksheet.merge_range(9, 0, 10, 1, "الوصف", table_header)
            worksheet.merge_range(9, 2, 10, 2, "وحدة القياس", table_header)
            worksheet.merge_range(9, 3, 9, 5, "الكمية", table_header)
            worksheet.write(10, 3, "الكمية السابقة", table_header)
            worksheet.write(10, 4, "الكمية الحالية", table_header)
            worksheet.write(10, 5, "الاجمالي", table_header)
            worksheet.merge_range(9, 6, 10, 6, "سعر الوحدة", table_header)
            worksheet.merge_range(9, 7, 10, 7, "المبلغ", table_header)
            row = 11
            for line in inv.invoice_line_ids:
                worksheet.merge_range(row, 0, row, 1, line.name, table_content)
                worksheet.write(row, 2, line.uom_id.name, table_content)
                worksheet.write(row, 3, line.previous_qty, table_content)
                worksheet.write(row, 4, line.quantity, table_content)
                worksheet.write(row, 5, line.quantity + line.previous_qty, table_content)
                worksheet.write(row, 6, "{} {}".format(line.price_unit, line.currency_id.symbol), table_content)
                worksheet.write(row, 7, "{} {}".format(line.price_subtotal, line.currency_id.symbol), table_content)
                row += 1

            row += 3
            worksheet.write(row, 6, "الاجمالي", table_header)
            worksheet.write(row, 7, "{} {}".format(inv.amount_total, inv.currency_id.symbol), table_content)
            row += 1
            worksheet.write(row, 6, "المدفوع", table_header)
            worksheet.write(row, 7, "{} {}".format(inv.amount_total - inv.residual, inv.currency_id.symbol),
                            table_content)
            row += 1
            worksheet.write(row, 6, "المتبقي", table_header)
            worksheet.write(row, 7, "{} {}".format(inv.residual, inv.currency_id.symbol), table_content)

    def table_header_format(self, workbook):
        return workbook.add_format({
            'bold': 1,
            'border': 0,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#13024f',
            'font_color': 'white',

        })

    def table_header_format2(self, workbook):
        return workbook.add_format({
            'bold': 1,
            'border': 0,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#7c7d7c',
            'font_color': 'white',

        })

    def table_content_format(self, workbook):
        return workbook.add_format({
            'bold': 1,
            'border': 0,
            'font_size': 10,
            'align': 'center',
            'font_color': 'blue',
        })

    def header_format(self, workbook):
        return workbook.add_format({
            'font_size': 16,
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#13024f',
            'bold': True
        })

    def header2_format(self, workbook):
        return workbook.add_format({
            'font_size': 14,
            'font_color': 'white',
            'align': 'center',
            'bg_color': '#13024f',
            'bold': True
        })
