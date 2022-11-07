# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.account'
    price_percent_inc = fields.Float('Limit Price Percent')
    qty_percent_inc = fields.Float(string='Limit Qty Percent')
