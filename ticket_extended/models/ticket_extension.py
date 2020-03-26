from odoo import api, models, fields

class HelpdeskTicketExtension(models.Model):
    _inherit='helpdesk.ticket'

    partner_street = fields.Char(string='Straße')
    partner_house_number = fields.Char(string='Hausnummer')
    partner_phone = fields.Char(string='Telefon')
    partner_data_protection = fields.Boolean(string='Datenschutz')

    @api.onchange('partner_id')
    def _onchange_partner_id_extended(self):
        if self.partner_id:
            self.partner_street = self.partner_id.street
            self.partner_house_number = self.partner_id.x_house_number
            self.partner_phone = self.partner_id.phone
            self.partner_data_protection = self.partner_id.x_data_protection


