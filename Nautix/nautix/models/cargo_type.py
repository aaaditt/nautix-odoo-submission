from odoo import models, fields


class NautixCargoType(models.Model):
    _name = 'nautix.cargo.type'
    _description = 'Cargo Type'

    name = fields.Char(string='Cargo Name', required=True)
    category = fields.Selection([
        ('dry_bulk', 'Dry Bulk'),
        ('liquid_bulk', 'Liquid Bulk'),
        ('break_bulk', 'Break Bulk'),
        ('containerized', 'Containerized'),
    ], string='Category')
    hazardous = fields.Boolean(string='Hazardous')
