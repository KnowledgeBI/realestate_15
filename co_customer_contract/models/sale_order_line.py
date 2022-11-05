# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_categ_id = fields.Many2one(comodel_name="product.category", string="Product Category", required=False, )
    cost_plus = fields.Float(string="Cost Plus", required=False)
    cost_plus_perc = fields.Float(string="Cost Plus %", required=False)
    unit_cost = fields.Float(string="Unit Cost", compute="_compute_unit_cost", store=True)
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)
    margin_perc = fields.Float(string="Margin(%)", required=False, )
    margin_price = fields.Float(string="Margin", compute="compute_margin_price", store=True)
    boq_line_ids = fields.One2many(comodel_name="boq.line", inverse_name="order_line_id", string="BOQ Lines",
                                   required=False, )

    @api.depends('boq_line_ids', 'boq_line_ids.subtotal_cost', 'product_uom_qty')
    def _compute_unit_cost(self):
        for line in self:
            total_cost = 0.0
            for boq_line in line.boq_line_ids:
                total_cost += boq_line.subtotal_cost
            line.unit_cost = total_cost / line.product_uom_qty

    @api.onchange('margin_perc', 'total_cost')
    def onchange_margin_perc(self):
        self.price_unit = (self.margin_perc / 100) * self.total_cost + self.total_cost

    def get_manual_unit_price(self):
        return (self.margin_perc / 100) * self.total_cost + self.total_cost

    @api.onchange('cost_plus_perc', 'unit_cost')
    def onchange_cost_plus_perc(self):
        self.cost_plus = (self.cost_plus_perc / 100) * self.unit_cost

    @api.depends('unit_cost', 'cost_plus')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.unit_cost + line.cost_plus

    @api.depends('total_cost', 'product_uom_qty', 'margin_perc')
    def compute_margin_price(self):
        for line in self:
            line.margin_price = (line.margin_perc / 100) * line.total_cost * line.product_uom_qty

    @api.onchange('product_categ_id')
    def onchange_product_categ_id(self):
        all_child_ids = self.env['product.category'].search([('parent_id', 'child_of', self.product_categ_id.id)])
        return {
            'domain': {
                'product_id': [('categ_id', 'in', all_child_ids.ids)]
            }
        }
    def _compute_tax_id(self):
        for line in self:
            if not self.env.context.get('general_taxes'):
                line = line.with_company(line.company_id)
                fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(line.order_partner_id.id)
                # If company_id is set, always filter taxes by the company
                taxes = line.product_id.taxes_id.filtered(lambda t: t.company_id == line.env.company)
                line.tax_id = fpos.map_tax(taxes)


    def _get_display_price(self, product):
        unit_price = super(SaleOrderLine, self)._get_display_price(product)
        if self.margin_perc:
            unit_price = self.get_manual_unit_price()
        return unit_price

    def action_show_details(self):
        view = self.env.ref('co_customer_contract.order_line_show_details')
        return {
            'name': _('BOQ Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            # 'context': self.env.context,
        }
