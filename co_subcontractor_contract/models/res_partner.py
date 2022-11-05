# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_subcontractor = fields.Boolean('Is Subcontractor')
