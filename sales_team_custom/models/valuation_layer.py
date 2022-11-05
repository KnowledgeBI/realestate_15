# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class ValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    team_id = fields.Many2one(
        comodel_name="crm.team",
        string="Sales Team",
        related="stock_move_id.team_id",
        store=True,
    )
