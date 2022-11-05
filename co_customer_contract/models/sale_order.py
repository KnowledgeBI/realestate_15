# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_contract = fields.Boolean(string="Is Contract", )
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    cost_plus = fields.Float(string="Cost Plus", required=False, )
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)
    margin_perc = fields.Float(string="Margin", related='analytic_account_id.margin_perc', readonly=False, store=True)
    total_margin = fields.Monetary(string="Total Margin", required=False, compute="compute_total_margin", store=True)
    tax_ids = fields.Many2many(comodel_name="account.tax", string="Taxes", domain="[('type_tax_use', '=', 'sale')]")

    @api.onchange('cost_plus')
    def onchange_cost_plus(self):
        for line in self.order_line:
            line.cost_plus_perc = self.cost_plus
            line.onchange_cost_plus_perc()

    @api.onchange('margin_perc')
    def onchange_margin_perc(self):
        for line in self.order_line:
            line.margin_perc = self.margin_perc
            line.onchange_margin_perc()

    @api.depends('order_line', 'order_line.margin')
    def compute_total_margin(self):
        for order in self:
            total_margin = 0.0
            for line in order.order_line:
                total_margin += line.margin_price
            order.total_margin = total_margin

    @api.depends('order_line', 'order_line.total_cost')
    def _compute_total_cost(self):
        for order in self:
            total_cost = 0.0
            for line in order.order_line:
                total_cost += line.total_cost
            order.total_cost = total_cost

    def action_show_boq_lines(self):
        view = self.env.ref('co_customer_contract.boq_line_view_tree')
        return {
            'name': _('BOQ'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'boq.line',
            'views': [(view.id, 'tree')],
            'view_id': view.id,
            'target': 'current',
            'domain': [('order_line_id', 'in', self.order_line.ids)],
            'context': {
                'search_default_by_order_line_id': 1,
            },
        }

    @api.model
    def create(self, vals):
        if vals.get('is_contract'):
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.customer.contract') or _('New')
        new_record = super(SaleOrder, self).create(vals)
        return new_record
