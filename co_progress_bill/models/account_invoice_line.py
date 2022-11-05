# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    def calc_previous_qty(self, line, type):
        if type == 'purchase':
            if line:
                previous_qty = sum(
                    line.invoice_lines.mapped('quantity'))
                return previous_qty
            else:
                return 0.0
        else:
            if line:
                previous_qty = sum(
                    line.invoice_line_ids.mapped('quantity'))
                return previous_qty
            else:
                return 0.0

    order_qty = fields.Float(string="Order Qty")
    previous_qty = fields.Float(string="Previous Qty", required=False)
    total_qty = fields.Float(string="Total Qty", compute="_calc_total_qty", store=True)
    done_percent = fields.Float(string="Done Percent(%)", required=False, )
    sale_line_id = fields.Many2one(comodel_name="sale.order.line", string="Sale Line", required=False, )

    @api.depends('previous_qty', 'quantity')
    def _calc_total_qty(self):
        for line in self:
            line.total_qty = line.previous_qty + line.quantity
