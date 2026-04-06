# this model tracks cargo loading and discharge locations globally
from odoo import models, fields


class NautixPort(models.Model):
    _name = 'nautix.port'
    _description = 'Port'

    name = fields.Char(string='Port Name', required=True)
    country_id = fields.Many2one('res.country', string='Country')
    unlocode = fields.Char(string='UN/LOCODE')
    port_type = fields.Selection([
        ('dry_bulk', 'Dry Bulk'),
        ('liquid', 'Liquid'),
        ('container', 'Container'),
        ('general', 'General'),
    ], string='Port Type')
