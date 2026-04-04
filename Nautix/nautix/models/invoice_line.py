from odoo import models, fields, api


class NautixInvoiceLine(models.Model):
    _name = 'nautix.invoice.line'
    _description = 'Charter Invoice Line'

    charter_id = fields.Many2one(
        'nautix.charter', string='Charter',
        required=True, ondelete='cascade',
    )
    period_from = fields.Date(string='Period From')
    period_to = fields.Date(string='Period To')
    hire_days = fields.Float(
        string='Hire Days',
        compute='_compute_hire_days', store=True,
    )
    hire_rate = fields.Float(
        string='Daily Hire Rate',
        related='charter_id.hire_rate', store=True,
    )
    total_hire = fields.Float(
        string='Total Hire',
        compute='_compute_total_hire', store=True,
    )
    invoice_id = fields.Many2one('account.move', string='Invoice')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='charter_id.currency_id',
    )

    @api.depends('period_from', 'period_to')
    def _compute_hire_days(self):
        for rec in self:
            if rec.period_from and rec.period_to:
                rec.hire_days = (rec.period_to - rec.period_from).days
            else:
                rec.hire_days = 0

    @api.depends('hire_days', 'hire_rate')
    def _compute_total_hire(self):
        for rec in self:
            rec.total_hire = rec.hire_days * rec.hire_rate
