# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_invoice(self):
        vals = super(PurchaseOrder, self)._prepare_invoice()
        vals.update({
            'is_progress_bill': True,
            'account_analytic_id': self.account_analytic_id.id,
        })
        return vals

    def action_view_invoice(self, invoices=False):
        action = super(PurchaseOrder, self).action_view_invoice(invoices)
        if self.env.context.get('progress_bill'):
            if not invoices:
                # Invoice_ids may be filtered depending on the user. To ensure we get all
                # invoices related to the purchase order, we read them in sudo to fill the
                # cache.
                self.sudo()._read(['invoice_ids'])
                invoices = self.invoice_ids

            action = self.env.ref('co_progress_bill.action_move_in_invoice_type').sudo()
            result = action.read()[0]
            create_bill = self.env.context.get('create_bill', False)
            # override the context to get rid of the default filtering
            result['context'] = {
                'move_type': 'in_invoice',
                'default_purchase_id': self.id,
                'default_account_analytic_id': self.account_analytic_id.id,
                'default_is_progress_bill': True,
                'default_origin': self.name,
                'default_reference': self.partner_ref,
                'default_currency_id': self.currency_id.id,
                'default_company_id': self.company_id.id,
                'company_id': self.company_id.id
            }
            # choose the view_mode accordingly
            if len(invoices) > 1 and not create_bill:
                result['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                res = self.env.ref('co_progress_bill.view_move_form_bill', False)
                form_view = [(res and res.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
                else:
                    result['views'] = form_view
                result['res_id'] = invoices.id
            else:
                result = {'type': 'ir.actions.act_window_close'}

            return result

        return action




class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move=False):
        data = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        if self.order_id.is_contract:
            invoice_line = self.env['account.move.line']
            data.update({
                'quantity': 0.0,
                'order_qty': self.product_qty,
                'previous_qty': invoice_line.calc_previous_qty(self, 'purchase'),
            })
        return data
