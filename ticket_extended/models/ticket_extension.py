from odoo import api, models, fields

class HelpdeskTicketExtension(models.Model):
    _inherit='helpdesk.ticket'

    partner_street = fields.Char(string='Straße')
    partner_house_number = fields.Char(string='Hausnummer')
    partner_phone = fields.Char(string='Telefon')
    partner_data_protection = fields.Boolean(string='Datenschutz')


