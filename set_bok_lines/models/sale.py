# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class SO(models.Model):
    _inherit = 'sale.order'

    def action_view_purchases(self):
        return {
            'name': 'Purchases',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'context': {'create':0,'delete':0},
            'domain':[('so_id','=',self.id)],
            'target': 'current',
        }
    def action_view_pr(self):
        return {
            'name': 'Purchase Agreements',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'context': {'create':0,'delete':0},
            'domain':[('so_id','=',self.id)],
            'target': 'current',
        }
    def action_view_outs(self):
        return {
            'name': 'Picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'context': {'create':0,'delete':0},
            'domain':[('so_id','=',self.id)],
            'target': 'current',
        }
    # def action_view_subcontractor(self):
    #     return {
    #         'name': 'Contract',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'subcontract.requisition',
    #         'context': {'create':0,'delete':0},
    #         'domain':[('so_id','=',self.id)],
    #         'target': 'current',
    #     }
