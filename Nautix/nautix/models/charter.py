from odoo import models, fields, api


class NautixCharter(models.Model):
    _name = 'nautix.charter'
    _description = 'Charter'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        readonly=True,
        default='/',
        copy=False,
    )
    vessel_id = fields.Many2one(
        'nautix.vessel', string='Vessel', required=True, tracking=True,
    )
    charterer_id = fields.Many2one(
        'res.partner', string='Charterer', required=True,
        domain=[('is_company', '=', True)], tracking=True,
    )
    owner_id = fields.Many2one(
        'res.partner', string='Owner', required=True, tracking=True,
    )
    charter_type = fields.Selection([
        ('voyage_charter', 'Voyage Charter'),
        ('time_charter', 'Time Charter'),
        ('bareboat', 'Bareboat'),
        ('coa', 'Contract of Affreightment'),
    ], string='Charter Type', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('negotiation', 'Negotiation'),
        ('fixed', 'Fixed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    hire_rate = fields.Float(string='Daily Hire Rate')
    lump_sum_freight = fields.Float(string='Lump Sum Freight')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.ref('base.USD', raise_if_not_found=False),
    )
    laycan_from = fields.Date(string='Laycan From')
    laycan_to = fields.Date(string='Laycan To')
    load_port_ids = fields.Many2many(
        'nautix.port', relation='charter_load_port_rel',
        column1='charter_id', column2='port_id',
        string='Load Ports',
    )
    discharge_port_ids = fields.Many2many(
        'nautix.port', relation='charter_discharge_port_rel',
        column1='charter_id', column2='port_id',
        string='Discharge Ports',
    )
    cargo_id = fields.Many2one('nautix.cargo.type', string='Cargo')
    cargo_quantity = fields.Float(string='Cargo Quantity')
    notes = fields.Text(string='Notes')
    voyage_ids = fields.One2many(
        'nautix.voyage', 'charter_id', string='Voyages',
    )
    invoice_line_ids = fields.One2many(
        'nautix.invoice.line', 'charter_id', string='Hire Invoice Lines',
    )

    # ---- Sequence override ----
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'nautix.charter'
                ) or '/'
        return super().create(vals_list)

    # ---- State machine ----
    def action_to_negotiation(self):
        for rec in self:
            rec.state = 'negotiation'

    def action_fix(self):
        for rec in self:
            rec.state = 'fixed'
            rec.vessel_id.status = 'on_charter'

    def action_activate(self):
        for rec in self:
            rec.state = 'active'

    def action_complete(self):
        for rec in self:
            rec.state = 'completed'
            rec.vessel_id.status = 'available'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
