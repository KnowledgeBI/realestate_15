# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoices = fields.One2many(comodel_name="account.move", inverse_name="sale_id", string="Invoices")
    invoice_num = fields.Integer(string="Invoices", compute="_calc_invoice_num", store=True)

    @api.depends('invoices')
    def _calc_invoice_num(self):
        for order in self:
            order.invoice_num = len(order.invoices.ids)

    def action_view_invoice(self):
        action = super(SaleOrder, self).action_view_invoice()
        if self.env.context.get('progress_bill'):
            action = self.env.ref('co_progress_bill.action_move_out_invoice_type')
            result = action.read()[0]
            create_invoice = self.env.context.get('create_invoice', False)
            # override the context to get rid of the default filtering
            result['context'] = {
                'default_move_type': 'out_invoice',
                'default_sale_id': self.id,
                'journal_type': 'sale',
                'default_is_progress_bill': True,
            }
            # choose the view_mode accordingly
            if len(self.invoices) > 1 and not create_invoice:
                result['domain'] = "[('id', 'in', " + str(self.invoices.ids) + ")]"
            else:
                res = self.env.ref('co_progress_bill.view_move_form_invoice', False)
                form_view = [(res and res.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
                else:
                    result['views'] = form_view
                # Do not set an invoice_id if we want to create a new bill.
                if not create_invoice:
                    result['res_id'] = self.invoices.id or False
            action = result
        return action

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'out_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': move_type,
            'narration': self.note,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (
                    self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.client_order_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'sale_id': self.id,
            'account_analytic_id': self.analytic_account_id.id,
            'is_progress_bill': True,
        }
        return invoice_vals
