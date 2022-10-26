# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models, tools, _

class repair_order(models.Model):
    _inherit = ['repair.order']

    building= fields.Many2one('building','Main Property', copy=False )

    product_id = fields.Many2one(
        'product.product', string='Sub Property',
        domain=[('product_tmpl_id.is_property', '=', True)],
        readonly=True, required=True, states={'draft': [('readonly', False)]}, check_company=True)

    @api.onchange('building')
    def onchange_building(self):
        if self.building:
            units = self.env['product.template'].search([('is_property', '=', True),('building_id', '=', self.building.id)])
            products = self.env['product.product'].search([('product_tmpl_id','in',units.ids)])
            return {'domain': {'product_id': [('id', 'in', products.ids)]}}
