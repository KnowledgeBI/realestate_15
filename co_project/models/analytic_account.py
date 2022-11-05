# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    is_project = fields.Boolean(string="Project", )
    picking_type_id = fields.Many2one(comodel_name="stock.picking.type", string="Operation Type", required=False, )
    parent_group_id = fields.Many2one(comodel_name="account.analytic.group", string="Parent Group",
                                      related="group_id.parent_id", store=True)
    margin_perc = fields.Float(string="Margin", required=False, )
