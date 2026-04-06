# this model stores physical specifications and availability for ships
from odoo import models, fields


class NautixVessel(models.Model):
    _name = 'nautix.vessel'
    _description = 'Vessel'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Vessel Name', required=True, tracking=True)
    imo_number = fields.Char(string='IMO Number', tracking=True)
    vessel_type = fields.Selection([
        ('bulk_carrier', 'Bulk Carrier'),
        ('tanker', 'Tanker'),
        ('container', 'Container'),
        ('lng', 'LNG'),
        ('roro', 'RoRo'),
    ], string='Vessel Type', tracking=True)
    flag_state = fields.Char(string='Flag State')
    year_built = fields.Integer(string='Year Built')
    dwt = fields.Float(string='DWT')
    grt = fields.Float(string='GRT')
    loa = fields.Float(string='LOA (m)')
    beam = fields.Float(string='Beam (m)')
    draft = fields.Float(string='Draft (m)')
    owner_id = fields.Many2one('res.partner', string='Owner')
    status = fields.Selection([
        ('available', 'Available'),
        ('on_charter', 'On Charter'),
        ('under_repair', 'Under Repair'),
        ('laid_up', 'Laid Up'),
    ], string='Status', default='available', tracking=True)
    classification_society = fields.Char(string='Classification Society')
    next_drydock = fields.Date(string='Next Drydock')
