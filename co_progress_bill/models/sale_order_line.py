# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    invoice_line_ids = fields.One2many(comodel_name="account.move.line", inverse_name="sale_line_id",
                                       string="Invoices Lines (Sale)")

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        invoice_line = self.env['account.move.line']
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.order_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': 0.0,
            'order_qty': self.product_uom_qty,
            'previous_qty': invoice_line.calc_previous_qty(self, 'sale'),
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            # 'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_id': self.id,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
        })
        return res
