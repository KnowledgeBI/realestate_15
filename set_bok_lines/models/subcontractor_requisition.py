# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class subcontract_requisition_line(models.Model):
    _inherit = 'subcontract.requisition.line'
    boq_line_id = fields.Many2one('boq.line',string='Boq Line Ref')
    boq_ref = fields.Char('Boq Ref')
    area_id = fields.Many2one('boq.area', string='Building')
    floor_id = fields.Many2one('boq.floor', string='Floor')
    def _prepare_subcontract_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(subcontract_requisition_line, self)._prepare_subcontract_order_line(name, product_qty, price_unit, taxes_ids)
        res.update({
            'boq_line_id':self.boq_line_id.id,
            'boq_ref':self.boq_ref,
            'area_id':self.area_id.id,
            'floor_id':self.floor_id.id,
        })
        return res
class subcontract_requisition(models.Model):
    _inherit = 'subcontract.requisition'

    def action_in_progress(self):
        for boq_line in self.line_ids.mapped('boq_line_id'):
            prev_qty = sum(self.env['subcontract.requisition.line'].search([('boq_line_id','=',boq_line.id)]).mapped('product_qty'))
            if prev_qty > boq_line.product_qty:
                if not self.env.user.has_group('set_bok_lines.group_over_boq_line'):
                    raise UserError("You can't confirm this order as you exceed allowed quantity in Boq Lines for product:{}\n"
                                    "only users with [group Confirm Over Boq Lines] can do this action".format(boq_line.product_id.name))
        super(subcontract_requisition, self).action_in_progress()
    is_boq_follow_up = fields.Boolean(string="BOQ Follow UP",related='account_analytic_id.is_boq_follow_up',store=True )
    so_id = fields.Many2one('sale.order',string='Contract')


    def set_bok_lines(self):
        return {
            'name': 'Select Boq Lines',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'set.boq.lines',
            'context': {'obj_id': self.id, 'default_analytic_account_id': self.account_analytic_id.id,'service_only':1,'form_view_ref':'set_bok_lines.view_form2'},
            'target': 'new',
        }