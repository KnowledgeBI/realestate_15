# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Move(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        rec = super(Move, self).create(vals)
        if rec.stock_move_id:
            rec.team_id = rec.stock_move_id.team_id.id
        return rec


class MoveLine(models.Model):
    _inherit = 'account.move.line'

    team_id = fields.Many2one(
        comodel_name="crm.team",
        string="Sales Team",
        related="move_id.team_id",
        store=True,
    )
