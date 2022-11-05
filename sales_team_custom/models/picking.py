# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class Picking(models.Model):
    _inherit = 'stock.picking'

    team_id = fields.Many2one(comodel_name="crm.team", string="Sales Team", required=False, )
