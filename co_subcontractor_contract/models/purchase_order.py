# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    category_id = fields.Many2one('category.order', 'Category')
    is_contract = fields.Boolean('Is Contract')

    @api.model
    def create(self, vals):
        if vals.get('is_contract'):
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.subcontractor.contract')
        new_record = super(PurchaseOrder, self).create(vals)
        return new_record

    @api.onchange('account_analytic_id')
    def onchange_account_analytic_id(self):
        for line in self.order_line:
            line.account_analytic_id = self.account_analytic_id.id
