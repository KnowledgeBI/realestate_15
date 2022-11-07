# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class subcontract_order_line(models.Model):
    _inherit = 'subcontract.order.line'
    boq_line_id = fields.Many2one('boq.line',string='Boq Line Ref')
    boq_ref = fields.Char('Boq Ref')
    area_id = fields.Many2one('boq.area', string='Building')
    floor_id = fields.Many2one('boq.floor', string='Floor')
class subcontract_requisition(models.Model):
    _inherit = 'subcontract.order'
    boq_id = fields.Many2one('sale.order.line',string='Boq Ref')

