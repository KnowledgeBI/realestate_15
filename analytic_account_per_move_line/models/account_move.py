""" Initialize Account Move """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class AccountMove(models.Model):
    """
        Inherit Account Move:
         -
    """
    _inherit = 'account.move'

    analytic_account_id = fields.Many2one(
        'account.analytic.account'
    )
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    @api.onchange('analytic_account_id', 'analytic_tag_ids',
                  # 'invoice_line_ids', 'line_ids'
                  )
    # @api.constrains('analytic_account_id', 'analytic_tag_ids', 'invoice_line_ids', 'line_ids')
    def _onchange_analytic_account_id(self):
        """ analytic_account_id """
        for rec in self:
            if rec.analytic_account_id:
                if rec.invoice_line_ids:
                    rec.invoice_line_ids.update({
                        'analytic_account_id': rec.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, rec.analytic_tag_ids.ids)],
                    })
                if rec.line_ids:
                    rec.line_ids.update({
                        'analytic_account_id': rec.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, rec.analytic_tag_ids.ids)],
                    })


class AccountMoveLine(models.Model):
    """
        Inherit Account Move Line:
         -
    """
    _inherit = 'account.move.line'

    @api.onchange('name')
    def _onchange_name(self):
        """ name """
        for rec in self:
            if rec.move_id and rec.move_id.analytic_account_id:
                rec.update({
                    'analytic_account_id': rec.move_id.analytic_account_id.id,
                    })
            if rec.move_id and rec.move_id.analytic_tag_ids:
                rec.update({
                    'analytic_tag_ids': [(6, 0, rec.move_id.analytic_tag_ids.ids)],
                    })