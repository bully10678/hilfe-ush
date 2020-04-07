import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)

class HelpdeskTicketExtension(models.Model):
    _inherit = 'helpdesk.ticket'

    partner_street = fields.Char(string='Straße', tracking=True, required=True, store=True)
    partner_house_number = fields.Char(string='Hausnummer', tracking=True, required=True, store=True)
    partner_phone = fields.Char(string='Telefon', tracking=True, required=True, store=True)
    partner_data_protection = fields.Boolean(string='Datenschutz', tracking=True, required=True, store=True)
    partner_first_name = fields.Char(string='Vorname', tracking=True, required=True, store=True)
    partner_trusted = fields.Boolean(string='Kontakt vertrauenswürdig/geprüft', tracking=True, required=True,
                                     store=True)
    partner_zip = fields.Char(string='PLZ', tracking=True, store=True)
    partner_city = fields.Char(string="Ort", tracking=True, store=True)


    @api.model
    def handle_team_type(self):
        # information taken out of the db, adjust if needed
        team_name = "Helfermeldungen"
        tag_name = "Helfer"
        # help_alerts_id = 8
        # volunteer_id = 5
        res_teams = self.env['helpdesk.team'].search([('name', '=like', team_name)])
        res_tags = self.env['helpdesk.tag'].search([('name', '=like', tag_name)])
        result_teams = []
        result_tags = []
        for eachid in res_teams:
            result_teams.append(eachid)
        for eachid in res_tags:
            result_tags.append(eachid)
        _logger.warning(result_teams)
        _logger.warning(result_tags)
        _logger.warning(self.team_id.id)
        if res_teams and len(res_teams) == 1 and self.team_id.id == result_teams[0].id:
            return result_tags[0] or False
        else:
            return False

    @api.onchange('team_id')
    def _onchange_team_id_init_tags(self):
        if self.handle_team_type():
            self.tag_ids = [(4,self.handle_team_type().id)]


    @api.onchange('partner_id')
    def _onchange_partner_id_extended(self):
        if self.partner_id and self.partner_id.x_first_name:
            self.partner_street = self.partner_id.street
            self.partner_house_number = self.partner_id.x_house_number
            self.partner_phone = self.partner_id.phone
            self.partner_data_protection = self.partner_id.x_data_protection
            self.partner_first_name = self.partner_id.w
            self.partner_trusted = self.partner_id.x_contact_trusted
            self.partner_zip = self.partner_id.zip
            self.partner_city = self.partner_id.city

    def save_customer_info(self):
        if self.partner_id:
            self.partner_id.street = self.partner_street
            self.partner_id.x_house_number = self.partner_house_number
            self.partner_id.phone = self.partner_phone
            self.partner_id.x_data_protection = self.partner_data_protection
            self.partner_id.x_first_name = self.partner_first_name
            self.partner_id.x_contact_trusted = self.partner_trusted
            self.partner_id.email = self.partner_email
            self.partner_id.zip = self.partner_zip
            self.partner_id.city = self.partner_city
        else:
            if self.partner_name:
                new_id = self.env['res.partner'].create({
                    'name': self.partner_name,
                    'street': self.partner_street,
                    'x_house_number': self.partner_house_number,
                    'phone': self.partner_phone,
                    'x_data_protection': self.partner_data_protection,
                    'x_first_name': self.partner_first_name,
                    'x_contact_trusted': self.partner_trusted,
                    'email': self.partner_email,
                    'city': self.partner_city,
                    'zip' : self.partner_zip
                })
                if new_id.name == self.partner_name:
                    self.partner_id = new_id

    def write(self, values):
        res = super(HelpdeskTicketExtension, self).write(values)
        self.save_customer_info()
        return res

