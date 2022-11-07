# -*- coding: utf-8 -*-

from odoo import fields, models, _,api,exceptions
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero
import logging
_logger = logging.getLogger(__name__)
from dateutil.relativedelta import relativedelta

class EquipmentTimeSheetLine(models.Model):
    _name = "equipment.timesheet.line"
    equipment_timesheet_id = fields.Many2one('equipment.timesheet',)
    product_id = fields.Many2one('product.product',string='Product')
    boq_line_id = fields.Many2one('boq.line',string='Boq Line')
    area_id = fields.Many2one('boq.area',string='Building')
    category_id = fields.Many2one('category.name',string='Category')
    floor_id = fields.Many2one('boq.floor',string='Floor')
    unit_cost = fields.Float(string='Cost')
    hour_no = fields.Float(string='Hour No')
    note = fields.Char(string='Description')
    date = fields.Date()
    total_cost = fields.Float(compute ='compute_total_cost',store=True,string='Total Cost')
    product_uom_id = fields.Many2one('uom.uom')
    @api.depends('unit_cost', 'hour_no')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.hour_no * rec.unit_cost
    @api.constrains('date')
    def check_date(self):
        for rec in self:
            if rec.date and rec.equipment_timesheet_id.date_from and rec.equipment_timesheet_id.date_to:
                if not(rec.date >=rec.equipment_timesheet_id.date_from and rec.date <= rec.equipment_timesheet_id.date_to):
                    raise UserError("Date In Lines must be in Date range of TimeSheet")

    weekday = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], string='Week Day', required=True)

    @api.onchange('date')
    @api.constrains('date')
    def onchange_date(self):
        for rec in self:
            if rec.date:
                rec.weekday = str(rec.date.weekday())


    check_in = fields.Float('Check In')
    check_out = fields.Float('Check Out')
    supervisor = fields.Char()
    engineer = fields.Char()
    @api.onchange('check_out','check_in')
    @api.constrains('check_out','check_in')
    def onchange_check_in_out(self):
        for rec in self:
            rec.hour_no = rec.check_out-rec.check_in
    currency_id = fields.Many2one('res.currency',string='Currency',related='equipment_timesheet_id.currency_id',stroe=True)
    @api.onchange('boq_line_id')
    def _onchange_boq_line_id(self):
        for rec in self:
            # rec.unit_cost = rec.boq_line_id.unit_cost
            rec.product_id = rec.boq_line_id.product_id.id
            rec.area_id = rec.boq_line_id.area_id.id
            rec.floor_id = rec.boq_line_id.floor_id.id
    @api.onchange('category_id')
    def _onchange_category_id(self):
        for rec in self:
            rec.unit_cost = rec.category_id.cost

class EquipmentTimeSheet(models.Model):
    _name = "equipment.timesheet"
    name = fields.Char()
    state = fields.Selection(string="", selection=[('draft', 'draft'), ('waiting', 'Waiting Approve'), ('approved', 'Approved'), ], required=False,default='draft' )
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    sale_order_id = fields.Many2one('sale.order',string='Sale Order')
    currency_id = fields.Many2one('res.currency',string='Currency')
    journal_id = fields.Many2one('account.journal',string='Journal')
    move_id = fields.Many2one('account.move',string='Move',copy=False)
    def action_create_entry(self):
        line_vals = []
        for line in self.line_ids:
            line_vals.append((
                    0, 0,
                    {'account_id': line.product_id.categ_id.property_account_expense_categ_id.id,
                     'product_id': line.product_id.id,
                     'name': line.note or self.name,
                     'analytic_account_id': self.analytic_account_id.id,
                     'debit': line.total_cost}))
        line_vals.append((0, 0, {'account_id': self.journal_id.default_credit_account_id.id,
                        'product_id': False,
                        'analytic_account_id': self.analytic_account_id.id,
                        'credit': self.total_cost}))
        move = self.env['account.move'].create({
            'date': fields.Datetime.now(),
            'ref': self.name,
            'move_type': 'entry',
            'analytic_account_id': self.analytic_account_id.id,

            'journal_id': self.journal_id.id,
            'line_ids': line_vals
        })
        move.action_post()
        self.move_id = move
    def action_request_approve(self):
        self.state = 'waiting'
    def action_approve(self):
        self.action_create_entry()
        self.state = 'approved'
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        for rec in self:
            rec.currency_id = rec.sale_order_id.currency_id.id
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    total_cost = fields.Float(compute ='compute_total_cost',store=True,string='Total Cost')
    total_hour_no = fields.Float(compute ='compute_total_hour_no',store=True,string='Total Number of Hours')
    total_day_no = fields.Float(compute ='compute_total_day_no',store=True,string='Total Number of Days')
    @api.depends('total_hour_no')
    def compute_total_day_no(self):
        for rec in self:
            rec.total_day_no = rec.total_hour_no/8

    @api.depends('line_ids','line_ids.hour_no','line_ids.unit_cost','line_ids.total_cost')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(x.hour_no * x.unit_cost for x in rec.line_ids)


    @api.depends('line_ids','line_ids.hour_no')
    def compute_total_hour_no(self):
        for rec in self:
            rec.total_hour_no = sum(rec.line_ids.mapped('hour_no'))
    line_ids = fields.One2many(comodel_name="equipment.timesheet.line", inverse_name="equipment_timesheet_id", string="Line", required=False, )

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise exceptions.ValidationError('Date from must be less than or equal date to !')
