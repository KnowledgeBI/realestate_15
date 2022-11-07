# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)
class PrLine(models.Model):
    _inherit = 'purchase.requisition.line'
    boq_line_id = fields.Many2one('boq.line',string='Boq Line')
    sale_line_id = fields.Many2one('sale.order.line',related='boq_line_id.order_line_id',store=True,string='Boq Line')
    area_id = fields.Many2one('boq.area', string='Building')
    floor_id = fields.Many2one('boq.floor', string='Floor')
    _sql_constraints = [
        ('boq_product_uniq', 'unique (boq_line_id,requisition_id, product_id)',
         'A product from same BoqLine  must be unique per Agreement !')]

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(PrLine, self)._prepare_purchase_order_line( name, product_qty, price_unit, taxes_ids)
        res.update({
            'boq_line_id':self.boq_line_id.id,
            'boq_ref':self.boq_ref,
            'area_id':self.area_id.id,
            'floor_id':self.floor_id.id,

                    })
        return res
class PR(models.Model):
    _inherit = 'purchase.requisition'
    @api.constrains('line_ids')
    def check_lines(self):
        for rec in self:
            if rec.analytic_account_id.is_boq_follow_up:
                if any(not x.boq_line_id.ids for x in rec.line_ids):
                    raise UserError("For Any Boq Follow Up Project All Lines Must be Set from boq lines")
    so_id = fields.Many2one('sale.order',string='Customer Contract')
    transfer_picking_type_id = fields.Many2one('stock.picking.type',string='Transfer Operation',domain=[('code','=','outgoing')])
    transfer_id = fields.Many2one('stock.picking',string='Transfer')
    def set_bok_lines(self):
        return {
            'name': 'Select Boq Lines',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'set.boq.lines',
            'context': {'obj_id': self.id,'show_contract':1, 'default_analytic_account_id': self.analytic_account_id.id,'form_view_ref':'set_bok_lines.view_form'},
            'target': 'new',
        }
    def action_in_progress(self):
        for line in self.line_ids:
            if line.account_analytic_id.is_boq_follow_up:
                if line.boq_line_id.remaining_qty < line.product_qty:
                    if not self.env.user.has_group('set_bok_lines.group_over_qty_boq_line'):
                        raise UserError("You can't submit this order as you exceed allowed quantity in Boq Lines for product:{}\n"
                                        "only users with [group Confirm Over Qty Boq Lines] can do this action".format(line.product_id.name))
                    else:
                        diff = line.product_qty - line.boq_line_id.remaining_qty
                        inc_percent = diff/(line.boq_line_id.remaining_qty or 1)*100
                        if inc_percent > line.account_analytic_id.qty_percent_inc:
                            raise UserError(
                                "You can't submit this order as you exceed allowed Qty increasing percent defined in project in for product:{}".format(
                                    line.product_id.name))
                if line.boq_line_id.unit_cost < line.price_unit:
                    if not self.env.user.has_group('set_bok_lines.group_over_price_boq_line'):
                        raise UserError("You can't submit this order as you exceed allowed Price in Boq Lines for product:{}\n"
                                        "only users with [group Confirm Over Price Boq Lines] can do this action".format(line.product_id.name))
                    else:
                        diff = line.price_unit - line.boq_line_id.unit_cost
                        inc_percent = diff/(line.boq_line_id.unit_cost or 1)*100
                        if inc_percent > line.account_analytic_id.price_percent_inc:
                            raise UserError(
                                "You can't submit this order as you exceed allowed Price increasing percent defined in project in for product:{}".format(
                                    line.product_id.name))
            return super(PR, self).action_in_progress()
    def action_transfer(self):

        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        picking_type = self.transfer_picking_type_id
        asset_picking = Picking
        moves = Move

        if picking_type:

            picking_vals = {
                'origin': self.name ,
                'picking_type_id': picking_type.id,
                'company_id': self.company_id.id,
                'move_type': 'direct',
                'note': self.name or "",
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
                'partner_id': self.vendor_id.id ,
                'analytic_account_id': self.analytic_account_id.id,

            }

            Picking = Picking.create(picking_vals)
            for line in self.line_ids:
                move_vals = {
                    'name': self.name,
                    'product_uom': line.product_uom_id.id,
                    'picking_id': Picking.id,
                    'picking_type_id': picking_type.id,
                    'product_id': line.product_id.id,
                    'boq_line_id': line.boq_line_id.id,
                    'boq_ref': line.boq_ref,
                    'area_id': line.area_id.id,
                    'floor_id': line.floor_id.id,
                    'product_uom_qty': line.product_qty,
                    'state': 'draft',
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': picking_type.default_location_dest_id.id,
                    'analytic_account_id': line.account_analytic_id.id
                }

                moves |= Move.create(move_vals)
            Picking.action_confirm()
            Picking.action_assign()
            self.transfer_id = Picking.id

        return True