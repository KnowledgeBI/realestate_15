# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    team_id = fields.Many2one(
        comodel_name="crm.team",
        string="Sales Team",
        related="picking_id.team_id",
        store=True,
    )

    def _prepare_account_move_line(
            self, qty, cost, credit_account_id, debit_account_id, description
    ):
        self.ensure_one()
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id, description
        )
        for line in res:
            # Add Team in move line
            if self.team_id:
                line[2].update({"team_id": self.team_id.id})
        return res
