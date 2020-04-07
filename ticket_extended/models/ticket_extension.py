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
            self.partner_first_name = self.partner_id.x_first_name
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
                self.partner_id = self.env['res.partner'].create({
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

    def write(self, values):
        res = super(HelpdeskTicketExtension, self).write(values)
        self.save_customer_info()
        return res

    @api.model_create_multi
    def create(self, list_value):
        now = fields.Datetime.now()
        # determine user_id and stage_id if not given. Done in batch.
        teams = self.env['helpdesk.team'].browse([vals['team_id'] for vals in list_value if vals.get('team_id')])
        team_default_map = dict.fromkeys(teams.ids, dict())
        for team in teams:
            team_default_map[team.id] = {
                'stage_id': team._determine_stage()[team.id].id,
                'user_id': team._determine_user_to_assign()[team.id].id
            }

        # Manually create a partner now since 'generate_recipients' doesn't keep the name. This is
        # to avoid intrusive changes in the 'mail' module
        for vals in list_value:
            if 'partner_name' in vals and 'partner_email' in vals and 'partner_id' not in vals:
                vals['partner_id'] = self.env['res.partner'].create({
                    'name': vals['partner_name'],
                    'street': vals['partner_street'],
                    'x_house_number': vals['partner_house_number'],
                    'phone': vals['partner_phone'],
                    'x_data_protection': vals['partner_data_protection'],
                    'x_first_name': vals['partner_first_name'],
                    'email': vals['partner_email'],
                    'city': vals['partner_city'],
                    'zip' : vals['partner_zip']
                }).id

        # determine partner email for ticket with partner but no email given
        partners = self.env['res.partner'].browse([vals['partner_id'] for vals in list_value if
                                                   'partner_id' in vals and vals.get(
                                                       'partner_id') and 'partner_email' not in vals])
        partner_email_map = {partner.id: partner.email for partner in partners}
        partner_name_map = {partner.id: partner.name for partner in partners}

        for vals in list_value:
            if vals.get('team_id'):
                team_default = team_default_map[vals['team_id']]
                if 'stage_id' not in vals:
                    vals['stage_id'] = team_default['stage_id']
                # Note: this will break the randomly distributed user assignment. Indeed, it will be too difficult to
                # equally assigned user when creating ticket in batch, as it requires to search after the last assigned
                # after every ticket creation, which is not very performant. We decided to not cover this user case.
                if 'user_id' not in vals:
                    vals['user_id'] = team_default['user_id']
                if vals.get(
                        'user_id'):  # if a user is finally assigned, force ticket assign_date and reset assign_hours
                    vals['assign_date'] = fields.Datetime.now()
                    vals['assign_hours'] = 0

            # set partner email if in map of not given
            if vals.get('partner_id') in partner_email_map:
                vals['partner_email'] = partner_email_map.get(vals['partner_id'])
            # set partner name if in map of not given
            if vals.get('partner_id') in partner_name_map:
                vals['partner_name'] = partner_name_map.get(vals['partner_id'])

            if vals.get('stage_id'):
                vals['date_last_stage_update'] = now

        # context: no_log, because subtype already handle this
        tickets = super(HelpdeskTicketExtension, self).create(list_value)

        # make customer follower
        for ticket in tickets:
            if ticket.partner_id:
                ticket.message_subscribe(partner_ids=ticket.partner_id.ids)

        # apply SLA
        tickets.sudo()._sla_apply()

        return tickets