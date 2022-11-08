# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class AccountMove(models.Model):
    _inherit = 'account.move'
    # analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True)
    # @api.model
    # def create(self, vals):
    #     move_id = super(AccountMove, self).create(vals)
    #     if move_id.stock_move_id:
    #         move_id.account_analytic_id = move_id.stock_move_id.analytic_account_id.id
    #     return move_id
