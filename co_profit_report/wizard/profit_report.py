# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
import base64
import xlsxwriter
import io


class ProfitHistory(models.TransientModel):
    _name = 'profit.history'
    _description = 'Profit Profit'

    account_id = fields.Many2one(comodel_name="account.account")
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account")
    balance = fields.Float(string="Balance")


class ProfitReport(models.TransientModel):
    _name = 'profit.report'
    _description = 'Profit Report'

    date_from = fields.Date(string="Date From", required=False, default=date.today())
    date_to = fields.Date(string="Date To", required=False, default=date.today())
    analytic_ids = fields.Many2many(comodel_name="account.analytic.account", string="Projects",
                                    domain=[('is_project', '=', True)])
    excel_sheet = fields.Binary()

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise exceptions.ValidationError('Date from must be less than or equal date to !')

    def get_data(self, cost_of_revenue, expenses, analytics):
        if cost_of_revenue and expenses:
            sql = """
                SELECT 
                    aml.analytic_account_id,
                    aml.account_id,
                    SUM(aml.balance) as balance
                FROM 
                    account_move_line as aml
                WHERE 
                    aml.user_type_id in %s
                    AND aml.analytic_account_id in %s
                    AND aml.date >= %s
                    AND aml.date <= %s
                GROUP BY 
                    aml.analytic_account_id,
                    aml.account_id
                ORDER BY 
                    aml.analytic_account_id
            """
            self._cr.execute(sql, (
                (cost_of_revenue.id, expenses.id),
                tuple(analytics.ids),
                self.date_from,
                self.date_to
            ))
            items = self._cr.dictfetchall()
            return self.env['profit.history'].create(items)

    def action_print_xlsx(self):
        analytics = self.env['account.analytic.account'].search([('is_project', '=', True)])
        cost_of_revenue = self.env.ref('account.data_account_type_direct_costs')
        expenses = self.env.ref('account.data_account_type_expenses')
        result = self.get_data(cost_of_revenue, expenses, analytics)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        analytic_to_show = self.env['account.analytic.account']
        if self.analytic_ids:
            analytic_to_show |= self.analytic_ids
        else:
            analytic_to_show |= analytics
        self.write_cost_of_revenue(workbook,
                                   result.filtered(lambda
                                                       l: l.account_id.user_type_id.id == cost_of_revenue.id and l.analytic_account_id.id in analytic_to_show.ids),
                                   analytic_to_show)
        total_expenses = self.write_expenses(workbook,
                                             result.filtered(lambda
                                                                 l: l.account_id.user_type_id.id == expenses.id))
        self.write_final_report(workbook, result.filtered(lambda l: l.account_id.user_type_id.id == cost_of_revenue.id),
                                total_expenses)
        workbook.close()
        output.seek(0)
        self.write({'excel_sheet': base64.encodestring(output.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'Product Details',
            'url': '/web/content/profit.report/%s/excel_sheet/Profit Report.xlsx?download=true' % (
                self.id),
            'target': 'new'
        }

    def write_cost_of_revenue(self, workbook, items, analytics):
        table_header = self.table_header_format(workbook)
        table_header2 = self.table_header_format2(workbook)
        table_content = self.table_content_format(workbook)
        date_format_bold = workbook.add_format({'num_format': 'YYYY-MM-DD', 'bold': True})
        counter = 1
        for analytic in analytics:
            item_to_used = items.filtered(lambda l: l.analytic_account_id.id == analytic.id)
            if item_to_used:
                worksheet = workbook.add_worksheet("{}-{}".format(counter, analytic.name))
                counter += 1
                worksheet.right_to_left()
                worksheet.merge_range(0, 0, 1, 3, "تقـريـــر الاربـــــــاح التقديرية", self.header_format(workbook))
                worksheet.merge_range(2, 0, 3, 3, "من تاريخ {} إلي تاريخ {} العملة جنية مصري".format(self.date_from,
                                                                                                     self.date_to),
                                      self.header2_format(workbook))
                worksheet.write(4, 0, "المـشـــــــــروع", table_header2)
                worksheet.write(4, 1, analytic.name, table_content)
                worksheet.write(4, 2, "هامش الريح", table_header2)
                worksheet.write(4, 3, analytic.margin_perc, table_content)
                worksheet.set_column(0, 0, 40)
                worksheet.set_column(1, 4, 25)
                row = 5
                worksheet.write(row, 0, "الحســـاب", table_header)
                worksheet.write(row, 1, "الرصيـــد", table_header)
                worksheet.write(row, 2, "الهامش", table_header)
                worksheet.write(row, 3, "الاجمالي", table_header)
                row += 1
                total_balance = 0.0
                total_profit = 0.0
                all_total = 0.0
                for line in item_to_used:
                    worksheet.write(row, 0, line.account_id.name or 'None', table_content)
                    worksheet.write(row, 1, line.balance or 'None', table_content)
                    profit = (analytic.margin_perc / 100) * line.balance
                    worksheet.write(row, 2, profit or 0.0, table_content)
                    worksheet.write(row, 3, line.balance + profit or 0.0, table_content)
                    total_balance += line.balance
                    total_profit += profit
                    all_total += line.balance + profit
                    row += 1
                worksheet.write(row, 0, "الاجمالي", table_header2)
                worksheet.write(row, 1, total_balance, table_header2)
                worksheet.write(row, 2, total_profit, table_header2)
                worksheet.write(row, 3, all_total, table_header2)

    def write_expenses(self, workbook, items):
        table_header = self.table_header_format(workbook)
        table_header2 = self.table_header_format2(workbook)
        table_content = self.table_content_format(workbook)
        worksheet = workbook.add_worksheet("مصروفات")
        worksheet.right_to_left()
        worksheet.merge_range(0, 0, 1, 1, "تقـريـــر الاربـــــــاح التقديرية", self.header_format(workbook))
        worksheet.merge_range(2, 0, 3, 1, "من تاريخ {} إلي تاريخ {} العملة جنية مصري".format(self.date_from,
                                                                                             self.date_to),
                              self.header2_format(workbook))
        worksheet.write(4, 0, "المـشـــــــــروع", table_header2)
        worksheet.write(4, 1, "بناء", table_content)
        worksheet.set_column(0, 0, 40)
        worksheet.set_column(1, 4, 25)
        row = 5
        worksheet.write(row, 0, "الحســـاب", table_header)
        worksheet.write(row, 1, "الرصيـــد", table_header)
        row += 1
        total_balance = 0.0
        for line in items:
            worksheet.write(row, 0, line.account_id.name or 'None', table_content)
            worksheet.write(row, 1, line.balance or 'None', table_content)
            total_balance += line.balance
            row += 1
        worksheet.write(row, 0, "الاجمالي", table_header2)
        worksheet.write(row, 1, total_balance, table_header2)
        return total_balance

    def write_final_report(self, workbook, items, total_expenses):
        table_header = self.table_header_format(workbook)
        table_header2 = self.table_header_format2(workbook)
        table_content = self.table_content_format(workbook)
        worksheet = workbook.add_worksheet("بيان")
        worksheet.right_to_left()
        worksheet.merge_range(0, 0, 1, 1, "تقـريـــر الاربـــــــاح التقديرية", self.header_format(workbook))
        worksheet.merge_range(2, 0, 3, 1, "من تاريخ {} إلي تاريخ {} العملة جنية مصري".format(self.date_from,
                                                                                             self.date_to),
                              self.header2_format(workbook))
        worksheet.set_column(0, 0, 40)
        worksheet.set_column(1, 1, 25)
        total_balance = 0.0
        total = 0.0
        for line in items:
            total_balance += line.balance
            total += line.balance + (line.balance * (line.analytic_account_id.margin_perc / 100))

        worksheet.write(4, 0, "تكاليف العمليات", table_content)
        worksheet.write(4, 1, round(total_balance, 2), table_content)
        worksheet.write(5, 0, "الايرادات", table_content)
        worksheet.write(5, 1, round(total, 2), table_content)
        worksheet.write(6, 0, "مجمل الربح من العمليات", table_content)
        worksheet.write(6, 1, round(total - total_balance, 2), table_content)
        worksheet.write(7, 0, "مصروفات إدارية وعمومية", table_content)
        worksheet.write(7, 1, round(total_expenses, 2), table_content)
        worksheet.write(8, 0, "صافي الربح المتوقع", table_header2)
        worksheet.write(8, 1, round((total - total_balance) - total_expenses, 2), table_header2)

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
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': '#7c7d7c',
            'font_color': 'white',

        })

    def table_content_format(self, workbook):
        return workbook.add_format({
            'bold': 1,
            'border': 0,
            'font_size': 10,
            'align': 'right',
            'font_color': 'blue',
        })

    def header_format(self, workbook):
        return workbook.add_format({
            'font_size': 16,
            'font_color': 'white',
            'align': 'center',
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
