from odoo import models, fields


class NautixVoyage(models.Model):
    _name = 'nautix.voyage'
    _description = 'Voyage'

    charter_id = fields.Many2one(
        'nautix.charter', string='Charter',
        required=True, ondelete='cascade',
    )
    vessel_id = fields.Many2one(
        'nautix.vessel', string='Vessel',
        related='charter_id.vessel_id', store=True, readonly=True,
    )
    departure_port_id = fields.Many2one('nautix.port', string='Departure Port')
    arrival_port_id = fields.Many2one('nautix.port', string='Arrival Port')
    etd = fields.Datetime(string='ETD')
    eta = fields.Datetime(string='ETA')
    atd = fields.Datetime(string='ATD')
    ata = fields.Datetime(string='ATA')
    status = fields.Selection([
        ('planned', 'Planned'),
        ('underway', 'Underway'),
        ('completed', 'Completed'),
    ], string='Status', default='planned')
