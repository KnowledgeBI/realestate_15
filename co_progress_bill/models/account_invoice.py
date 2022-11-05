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


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    account_analytic_id = fields.Many2one(comodel_name="account.analytic.account", string="Project",
                                          required=True)
    date_from = fields.Date(string="Date from", required=False, )
    date_to = fields.Date(string="Date to", required=False, )
    is_progress_bill = fields.Boolean(string="Is Progress Bill")
    sale_id = fields.Many2one(comodel_name="sale.order", string="Contract")
    progress_inv_excel_sheet = fields.Binary()
    previous_work = fields.Monetary(string="Previous Work", compute="_calc_previous_work", store=True)
    current_work = fields.Monetary(string="Current Work", compute="_calc_current_work", store=True)
    previous_payment = fields.Monetary(string="Previous Payments", compute="_calc_previous_payment", store=True)
    total_due = fields.Monetary(string="Total Due", compute="_calc_total_due", store=True)
    # team_id = fields.Many2one('crm.team',required=1,ondelete="set null")
    ##############################
    # TODO: Compute Methods
    ##############################
    
    def set_project_sector(self):
        """ Set Project Sector """
        for rec in self:
            if rec.invoice_line_ids:
                for line in rec.invoice_line_ids:
                    line.update({
                        'analytic_account_id': rec.account_analytic_id.id,
                        'team_id': rec.team_id.id,
                    })
                for line in rec.line_ids:
                    line.update({
                        'analytic_account_id': rec.account_analytic_id.id,
                        'team_id': rec.team_id.id,
                    })

    @api.depends(
        'amount_total',
        'previous_payment'
    )
    def _calc_total_due(self):
        for inv in self:
            inv.total_due = inv.amount_total - inv.previous_payment

    @api.onchange('account_analytic_id')
    def check_analytic_account(self):
        for rec in self:
            if rec.account_analytic_id:
                rec.team_id = rec.account_analytic_id.sale_team_id.id
                rec.set_project_sector()
            else:
                rec.team_id = False

    @api.depends('account_analytic_id','partner_id')
    def _calc_previous_payment(self):
        for inv in self:
            res = self.env['account.move.line'].search([
                ('partner_id', '=', inv.partner_id.id),
                ('analytic_account_id', '=', inv.account_analytic_id.id),
                ('account_id.user_type_id.type', '=', 'payable'),
                ('journal_id.type', 'in', ['bank', 'cash']),
            ]).mapped('balance')
            inv.previous_payment = sum([abs(b) for b in res])

    @api.depends(
        'invoice_line_ids.previous_qty',
        'invoice_line_ids.price_unit',
        'invoice_line_ids.discount'
    )
    def _calc_previous_work(self):
        for inv in self:
            inv.previous_work = sum(inv.invoice_line_ids.mapped(
                lambda line: line.previous_qty * (line.price_unit * (1 - (line.discount or 0.0) / 100.0))))

    @api.depends(
        'invoice_line_ids.quantity',
        'invoice_line_ids.price_unit',
        'invoice_line_ids.discount'
    )
    def _calc_current_work(self):
        for inv in self:
            inv.current_work = sum(inv.invoice_line_ids.mapped(
                lambda line: line.quantity * (line.price_unit * (1 - (line.discount or 0.0) / 100.0))))

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for bill in self:
            if bill.is_progress_bill:
                previous_bill = self.search([
                    ('partner_id', '=', bill.partner_id.id),
                    ('account_analytic_id', '=', bill.account_analytic_id.id),
                    ('purchase_id', '=', bill.purchase_id.id),
                    ('id', '!=', bill.id),
                ], order="date_from")
                if previous_bill:
                    if bill.date_from and previous_bill[-1].date_to:
                        if not bill.date_from > previous_bill[-1].date_to:
                            raise exceptions.ValidationError(
                                'Bill Date From must be greater than date to of last Bill {}!'.format(
                                    previous_bill[-1].date_to))
                if bill.date_from > bill.date_to:
                    raise exceptions.ValidationError('Date to must be greater than date from !')

    ##############################
    # Create Some Method to make
    # relation between sale order
    # and invoice
    ##############################

    @api.onchange('sale_id')
    def _onchange_sale_auto_complete(self):
        if not self.sale_id:
            return

        # Copy data from SO
        invoice_vals = self.sale_id.with_company(self.sale_id.company_id)._prepare_invoice()
        del invoice_vals['ref']
        self.update(invoice_vals)

        # Copy Sale lines.
        so_lines = self.sale_id.order_line - self.line_ids.mapped('sale_line_id')
        new_lines = self.env['account.move.line']
        for line in so_lines.filtered(lambda l: not l.display_type):
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped('sale_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Compute ref.
        refs = self._get_invoice_ref()
        self.ref = ', '.join(refs)

        # Compute payment_reference.
        if len(refs) == 1:
            self.payment_reference = refs[0]

        self._onchange_currency()
        self.partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]

    def _get_invoice_ref(self):
        self.ensure_one()
        vendor_refs = [ref for ref in set(self.line_ids.mapped('sale_line_id.order_id.client_order_ref')) if ref]
        if self.ref:
            return [ref for ref in self.ref.split(', ') if ref and ref not in vendor_refs] + vendor_refs
        return vendor_refs


