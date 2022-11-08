# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class BOQLine(models.Model):
    _inherit = 'boq.line'

    po_line_ids = fields.One2many(comodel_name="purchase.order.line", inverse_name="boq_line_id", string="", required=False, )
    purchase_qty = fields.Float('Purchase Qty',compute='compute_purchase_qty',store=True)
    ordered_qty = fields.Float('Ordered Qty')
    purchase_cost = fields.Float('Purchase Cost',compute='compute_purchase_qty',store=True)

    stockmove_ids = fields.One2many(comodel_name="stock.move", inverse_name="boq_line_id", string="", required=False, )
    project_out_qty = fields.Float('Project Out Qty', compute='compute_project_out_qty', store=True)
    project_cost = fields.Float('Project Cost', compute='compute_project_out_qty', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',related='order_line_id.order_id.analytic_account_id',store=True)

    # requisition_line_ids = fields.One2many(comodel_name="subcontract.requisition.line", inverse_name="boq_line_id", string="", required=False, )
    service_qty = fields.Float('Service Qty', store=True)
    service_cost = fields.Float('Service Cost',store=True)
    # service_qty = fields.Float('Service Qty', compute='compute_service_qty', store=True)
    # service_cost = fields.Float('Service Cost', compute='compute_service_qty', store=True)
    #
    remaining_qty = fields.Float('Remaining Qty', compute='compute_remain_qty', store=True)
    remaining_cost = fields.Float('Remaining Cost', compute='compute_remain_cost', store=True)
    @api.depends('purchase_qty','project_out_qty','service_qty','qty')
    def compute_remain_qty(self):
        for rec in self:
            rec.remaining_qty = rec.qty - (rec.purchase_qty + rec.project_out_qty + rec.service_qty)
    @api.depends('purchase_cost', 'project_cost', 'service_cost', 'subtotal_cost')
    def compute_remain_cost(self):
        for rec in self:
            rec.remaining_cost = rec.purchase_cost + rec.project_cost + rec.service_cost - rec.subtotal_cost
    @api.depends('po_line_ids','po_line_ids.state')
    def compute_purchase_qty(self):
        for boqline in self:
            tot = 0
            cost = 0
            for rec in boqline.po_line_ids:
                # if rec.state == 'purchase' and not rec.canceled:
                if rec.state == 'purchase' :
                    tot += rec.product_qty
                    cost += rec.price_total
            boqline.purchase_qty = tot
            boqline.purchase_cost = cost

    @api.depends('stockmove_ids','stockmove_ids.state')
    def compute_project_out_qty(self):
        for boqline in self:
            tot = 0
            cost = 0
            for rec in boqline.stockmove_ids:
                # if rec.state == 'done' and not rec.boq_line_id.canceled:
                if rec.state == 'done' :
                    tot += rec.quantity_done
                    cost += rec.price_unit
            boqline.project_out_qty = tot
            boqline.project_cost = cost

    # @api.depends('requisition_line_ids','requisition_line_ids.requisition_id.state')
    # def compute_service_qty(self):
    #     for boqline in self:
    #         tot = 0
    #         cost = 0
    #         for rec in boqline.requisition_line_ids:
    #             if rec.requisition_id.state in ['done','open','in_progress'] and not rec.boq_line_id.canceled:
    #                 tot += rec.qty_ordered
    #                 cost += rec.my_total
    #         boqline.service_qty = tot
    #         boqline.service_cost = cost

