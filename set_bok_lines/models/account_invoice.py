# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.addons.account.models.account_invoice import AccountInvoice
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    boq_line_id = fields.Many2one('boq.line',string='Boq Line Ref')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    def _prepare_invoice_line_from_co_line(self, line):
        data = super(AccountInvoice, self)._prepare_invoice_line_from_co_line(line)
        data.update({'boq_line_id': line.boq_line_id.id})
        return data


