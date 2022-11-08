# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class POLine(models.Model):
    _inherit = 'purchase.order.line'
    categ_id = fields.Many2one(comodel_name="product.category", string="Category", related='product_id.categ_id',
                               store=True)
    boq_line_id = fields.Many2one('boq.line',string='Boq Line Ref')
    boq_ref = fields.Char('Boq Ref')
    area_id = fields.Many2one('boq.area', string='Building')
    floor_id = fields.Many2one('boq.floor', string='Floor')
    _sql_constraints = [
        ('boq_product_uniq', 'unique (boq_line_id,order_id, product_id)',
         'A product from same BoqLine  must be unique per contract !')]
class PO(models.Model):
    _inherit = 'purchase.order'

    def action_submit(self):
        for line in self.order_line:
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

        return super(PO, self).action_submit()
    is_boq_follow_up = fields.Boolean(string="BOQ Follow UP",related='account_analytic_id.is_boq_follow_up',store=True )
    so_id = fields.Many2one('sale.order',string='Contract')


    def set_bok_lines(self):
        return {
            'name': 'Select Boq Lines',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'set.boq.lines',
            'context': {'obj_id': self.id,'show_contract':1, 'default_analytic_account_id': self.account_analytic_id.id,'form_view_ref':'set_bok_lines.view_form'},
            'target': 'new',
        }
