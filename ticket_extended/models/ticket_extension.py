from odoo import api, models, fields

class HelpdeskTicketExtension(models.Model):
    _inherit='helpdesk.ticket'

    partner_street = fields.Char(string='Straße', tracking=True, required=True, store=True)
    partner_house_number = fields.Char(string='Hausnummer', tracking=True, required=True, store=True)
    partner_phone = fields.Char(string='Telefon', tracking=True, required=True, store=True)
    partner_data_protection = fields.Boolean(string='Datenschutz', tracking=True, required=True, store=True)
    partner_first_name = fields.Char(string='Vorname', tracking=True, required=True, store=True)

    @api.onchange('partner_id')
    def _onchange_partner_id_extended(self):
        if self.partner_id:
            self.partner_street = self.partner_id.street
            self.partner_house_number = self.partner_id.x_house_number
            self.partner_phone = self.partner_id.phone
            self.partner_data_protection = self.partner_id.x_data_protection
            self.partner_first_name = self.partner_id.x_first_name

    def write(self, values):
        res = super(HelpdeskTicketExtension, self).write(values)
        self.partner_id.street = self.partner_street
        self.partner_id.x_house_number = self.partner_house_number
        self.partner_id.phone = self.partner_phone
        self.partner_id.x_data_protection = self.partner_data_protection
        self.partner_id.x_first_name = self.partner_first_name
        return res


