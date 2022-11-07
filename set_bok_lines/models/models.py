# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class SetBoqLines(models.TransientModel):
    _name = "set.boq.lines"
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', required=False,)
    line_ids = fields.Many2many('boq.line', string='Lines', required=False,)
    so_id = fields.Many2one('sale.order',string='Contract')
    @api.onchange('so_id')
    def _onchange_so(self):
        self.line_ids=False

    def action_reset_qty(self):
        for line in self.line_ids:
            line.ordered_qty = 0

    def apply(self):
        active_model = self.env.context.get('active_model')
        if active_model =='purchase.order':
            po = self.env['purchase.order'].browse(self.env.context.get('active_id'))
            new_list = []
            for line in self.line_ids:
                vals={
                    'product_id':line.product_id.id,
                    'categ_id':line.categ_id.id,
                    'name':line.name,
                    'account_analytic_id':line.analytic_account_id.id,
                    'product_qty':line.ordered_qty if line.ordered_qty <= line.qty else line.qty,
                    'product_uom':line.product_uom_id.id,
                    'date_planned':fields.Datetime.now(),
                    'price_unit':0.0,
                    'boq_line_id':line.id,
                    'area_id':line.area_id.id,
                    'floor_id':line.floor_id.id,
                    'boq_ref':line.boq_ref
                }
                new_list.append((0,0,vals))
            po.order_line = new_list
            po.so_id = self.so_id.id
        elif active_model =='stock.picking':
            picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
            new_list = []
            for line in self.line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    # 'categ_id': line.categ_id.id,
                    'name': line.name,
                    'analytic_account_id': line.analytic_account_id.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'product_uom_qty': line.ordered_qty if line.ordered_qty <= line.qty else line.qty,
                    'product_uom': line.product_uom_id.id,
                    # 'date_planned': fields.Datetime.now(),
                    'price_unit': line.unit_cost,
                    'boq_line_id': line.id,
                    'area_id': line.area_id.id,
                    'floor_id': line.floor_id.id,
                    'boq_ref': line.boq_ref

                }
                new_list.append((0, 0, vals))
            picking.move_ids_without_package = new_list
            picking.so_id = self.so_id.id

        elif active_model =='subcontract.requisition':
            sr = self.env['subcontract.requisition'].browse(self.env.context.get('active_id'))
            new_list = []
            for line in self.line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'description': line.name,
                    'account_analytic_id': line.analytic_account_id.id,
                    'product_qty': line.ordered_qty if line.ordered_qty <= line.qty else line.qty,
                    'product_uom_id': line.product_uom_id.id,
                    'price_unit': line.unit_cost,
                    'boq_line_id': line.id,
                    'area_id': line.area_id.id,
                    'floor_id': line.floor_id.id,
                    'boq_ref': line.boq_ref

                }
                new_list.append((0, 0, vals))
            sr.line_ids = new_list
            sr.so_id = self.so_id.id
        elif active_model =='purchase.requisition':
            pr = self.env['purchase.requisition'].browse(self.env.context.get('active_id'))
            new_list = []
            for line in self.line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'description': line.name,
                    'account_analytic_id': line.analytic_account_id.id,
                    'product_qty': line.ordered_qty if line.ordered_qty <= line.qty else line.qty,
                    'product_uom_id': line.product_uom_id.id,
                    # 'price_unit': line.unit_cost,
                    'boq_line_id': line.id,
                    'area_id': line.area_id.id,
                    'floor_id': line.floor_id.id,
                    'boq_ref': line.boq_ref

                }
                new_list.append((0, 0, vals))
            pr.line_ids = new_list
            pr.so_id = self.so_id.id


