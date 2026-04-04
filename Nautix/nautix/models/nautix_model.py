from odoo import models, fields


class NautixModel(models.Model):
    _name = 'nautix.model'
    _description = 'Nautix Model'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
