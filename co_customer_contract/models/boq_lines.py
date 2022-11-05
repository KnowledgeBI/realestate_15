# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class BOQLine(models.Model):
    _name = 'boq.line'
    _rec_name = 'name'
    _description = 'BOQ Lines'

    order_line_id = fields.Many2one(comodel_name="sale.order.line", string="Order Line", required=False, )
    area_id = fields.Many2one(comodel_name="boq.area", string="Area", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=True, )
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'product'),
    ], string='Product Type', related="product_id.type")
    name = fields.Char(string="Description", required=True, )
    qty = fields.Float(string="Total QTY", required=False, )
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="Unit Of Measure", required=True, )
    unit_cost = fields.Float(string="Unit Cost", required=False, )
    subtotal_cost = fields.Float(string="Total Cost", compute="_calc_subtotal_cost", store=True)

    @api.depends('unit_cost', 'qty')
    def _calc_subtotal_cost(self):
        for line in self:
            line.subtotal_cost = line.qty * line.unit_cost

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id.id


class Area(models.Model):
    _name = 'boq.area'
    _rec_name = 'name'
    _description = 'BOQ Area'

    name = fields.Char(string="Name", required=True)
