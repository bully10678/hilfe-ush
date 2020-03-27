from odoo import api, models, fields


class HelpdeskTicketExtension(models.Model):
    _inherit = 'helpdesk.ticket'

    partner_street = fields.Char(string='Straße', tracking=True, required=True, store=True)
    partner_house_number = fields.Char(string='Hausnummer', tracking=True, required=True, store=True)
    partner_phone = fields.Char(string='Telefon', tracking=True, required=True, store=True)
    partner_data_protection = fields.Boolean(string='Datenschutz', tracking=True, required=True, store=True)
    partner_first_name = fields.Char(string='Vorname', tracking=True, required=True, store=True)
    partner_trusted = fields.Boolean(string='Kontakt vertrauenswürdig/geprüft', tracking=True, required=True,
                                     store=True)

    @api.model
    def handle_team_type(self):
        # information taken out of the db, adjust if needed
        team_name = "Helfermeldungen"
        tag_name = "Helfer"
        # help_alerts_id = 8
        # volunteer_id = 5
        team_obj = self.pool.get('helpdesk.team')
        tag_obj = self.pool.get('helpdesk.tag')
        res_teams = team_obj.name_search(self,name=team_name)
        res_tags = tag_obj.name_search(self,name=tag_name)
        result_teams = []
        result_tags = []
        for eachid in res_teams:
            result_teams.append(eachid)
        for eachid in res_tags:
            result_tags.append(eachid)

        return result_tags or False

    tag_ids = fields.Many2many('helpdesk.tag', string='Tags_debug', default=handle_team_type)

    @api.onchange('partner_id')
    def _onchange_partner_id_extended(self):
        if self.partner_id:
            self.partner_street = self.partner_id.street
            self.partner_house_number = self.partner_id.x_house_number
            self.partner_phone = self.partner_id.phone
            self.partner_data_protection = self.partner_id.x_data_protection
            self.partner_first_name = self.partner_id.x_first_name
            self.partner_trusted = self.partner_id.x_contact_trusted

    def save_customer_info(self):
        self.partner_id.street = self.partner_street
        self.partner_id.x_house_number = self.partner_house_number
        self.partner_id.phone = self.partner_phone
        self.partner_id.x_data_protection = self.partner_data_protection
        self.partner_id.x_first_name = self.partner_first_name
        self.partner_id.x_contact_trusted = self.partner_trusted

    def write(self, values):
        res = super(HelpdeskTicketExtension, self).write(values)
        self.save_customer_info()
        return res
