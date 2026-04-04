from odoo import api, models, fields
from odoo.exceptions import UserError
class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'

    name = fields.Char(string='Title', required=True)
    description = fields.Text()
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    has_garden = fields.Boolean()
    garden_area = fields.Integer()
    total_area = fields.Integer(compute='_compute_total_area')
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    offers_ids = fields.One2many('estate.property.offers', 'property_id', string='Offers')
    best_price = fields.Float(compute='_compute_best_price', string='Best Offer')
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], default='new', string='Status')
    _check_expected_price = ['expected_price > 0']

    @api.depends('offers_ids.price')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offers_ids.mapped('price')) if record.offers_ids else 0.0


    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area


    def sell_property(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError('A canceled property cannot be sold.')
            if record.best_price >= record.expected_price:
                record.selling_price = record.best_price
                record.state = 'sold'
            else:
                raise UserError('The best offer must be greater than or equal to the expected price to sell the property.')
            
    def cancel_sale(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('A sold property cannot be canceled.')
            record.selling_price = 0.0
            record.buyer_id = False
            record.state = 'canceled'

    