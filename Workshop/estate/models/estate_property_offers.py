from odoo import api, fields, models

class EstatePropertyOffers(models.Model):
    _name = 'estate.property.offers'
    _description = 'Estate Property Offers'

    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], default='accepted')
    partner_id = fields.Many2one('res.partner', required=True, string='Partner')
    property_id = fields.Many2one('estate.property', string='Property')
    validity = fields.Integer(string='Validity (days)')

    def accept_offer(self):
        for offer in self:
            offer.status = 'accepted'
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price
            offer.property_id.state = 'offer_accepted'

    def refuse_offer(self):
        for offer in self:
            offer.status = 'refused'

    @api.model
    def create(self, vals):
        record = super(EstatePropertyOffers, self).create(vals)
        if record.property_id:
            record.property_id.state = 'offer_received'
            if record.property_id.expected_price and record.price >= record.property_id.expected_price:
                record.status = 'accepted'
                record.property_id.buyer_id = record.partner_id
                record.property_id.selling_price = record.price
                record.property_id.state = 'offer_accepted'
        return record