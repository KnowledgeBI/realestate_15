# -*- coding: utf-8 -*-

from odoo import fields, models, _,api,exceptions
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero
import logging
_logger = logging.getLogger(__name__)

class Category(models.Model):
    _name = "category.name"
    name = fields.Char()
    cost = fields.Float()
