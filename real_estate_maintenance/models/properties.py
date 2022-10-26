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
from odoo.exceptions import ValidationError
from odoo import api, fields, models, tools, _

class building(models.Model):
    _description = "Building"
    _inherit = ['building']

    def _maintenance_count(self):
        maintenance_obj = self.env['repair.order']
        for building in self:
            maintenance_ids = maintenance_obj.search([('building', '=', building.id)])
            building.maintenance_count = len(maintenance_ids)

    maintenance_count= fields.Integer(compute='_maintenance_count',string='Maintenance Count',)

    def view_maintenance(self):
        maintenance_obj = self.env['repair.order']
        maintenance_ids = maintenance_obj.search([('building', 'in', self.ids)])

        return {
            'name': _('Maintenance Requests'),
            'domain': [('id', 'in', maintenance_ids.ids)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'repair.order',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'view_id': False,
            'target':'current',
        }

class building_unit(models.Model):
    _inherit = ['product.template']

    def _maintenance_count(self):
        maintenance_obj = self.env['repair.order']
        for unit in self:
            maintenance_ids = maintenance_obj.search([('product_id.product_tmpl_id', '=', unit.id)])
            unit.maintenance_count = len(maintenance_ids)

    maintenance_count = fields.Integer(compute='_maintenance_count', string='Maintenance Count', )

    def view_maintenance(self):
        maintenance_obj = self.env['repair.order']
        maintenance_ids = maintenance_obj.search([('product_id.product_tmpl_id', 'in', self.ids)])

        return {
            'name': _('Maintenance Requests'),
            'domain': [('id', 'in', maintenance_ids.ids)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'repair.order',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'view_id': False,
            'target': 'current',
        }
