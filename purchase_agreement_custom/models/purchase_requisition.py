# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
PURCHASE_REQUISITION_STATES = [
    ('draft', 'Draft'),
    ('ongoing', 'Ongoing'),
    ('in_progress', 'Confirmed'),
    ('proc_approve', 'procurement Approve'),
    ('open', 'Bid Selection'),
    ('done', 'Closed'),
    ('cancel', 'Cancelled')
]
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    category = fields.Selection(string="Category", selection=[("Civil","Civil"),("Mechanical","Mechanical"),("Electrical","Electrical"),("IT","IT"),("Other","Other")], required=False, )
    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        super(PurchaseOrder, self)._onchange_requisition_id()
        self.category = self.requisition_id.category
        self.account_analytic_id = self.requisition_id.analytic_account_id.id
        self.so_id = self.requisition_id.so_id.id

class PurchaseRequisitionline(models.Model):
    _inherit = 'purchase.requisition.line'
    boq_ref = fields.Char()
    description = fields.Char()

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(PurchaseRequisitionline, self)._prepare_purchase_order_line(name, product_qty, price_unit, taxes_ids)
        res.update({
            'name':self.description,
        })
        return res
class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    category = fields.Selection(string="Category", selection=[("Civil","Civil"),("Mechanical","Mechanical"),("Electrical","Electrical"),("IT","IT"),("Other","Other")], required=False, )
    analytic_account_id = fields.Many2one('account.analytic.account',string='Project')
    state = fields.Selection(PURCHASE_REQUISITION_STATES)
    state_blanket_order = fields.Selection(PURCHASE_REQUISITION_STATES)
    def proc_approve(self):
        self.state = 'proc_approve'
    @api.onchange('analytic_account_id')
    def onchange_method(self):
        self.picking_type_id = self.analytic_account_id.picking_type_id.id
