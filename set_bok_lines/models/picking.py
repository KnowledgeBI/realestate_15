# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)
class move(models.Model):
    _inherit = 'stock.move'
    boq_line_id = fields.Many2one('boq.line',string='Boq Line Ref')
    boq_ref = fields.Char('Boq Ref')
    area_id = fields.Many2one('boq.area', string='Building')
    floor_id = fields.Many2one('boq.floor', string='Floor')
class Picking(models.Model):
    _inherit = 'stock.picking'

    is_boq_follow_up = fields.Boolean(string="BOQ Follow UP",related='analytic_account_id.is_boq_follow_up',store=True )
    so_id = fields.Many2one('sale.order',string='Contract')


    def set_bok_lines(self):
        return {
            'name': 'Select Boq Lines',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'set.boq.lines',
            'context': {'obj_id': self.id, 'default_analytic_account_id': self.analytic_account_id.id,'form_view_ref':'set_bok_lines.view_form'},
            'target': 'new',
        }
