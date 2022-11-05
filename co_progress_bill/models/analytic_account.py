# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
import base64
import xlsxwriter
import io

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    sale_team_id = fields.Many2one('crm.team', string='Sales Team')
