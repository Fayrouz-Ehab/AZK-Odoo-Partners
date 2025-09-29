from odoo import models, fields, api


class Country(models.Model):
    _name = 'partner.country'
    _description = 'Odoo Partner Country'

    name = fields.Char(string='Country Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    slug = fields.Char()
    page_id = fields.Char()

    total_partner_count = fields.Integer(
        string='Total Partner Count',
        compute="_compute_partner_counts",
        store=True
    )
    to_reprocess_partners = fields.Boolean(string='To Reprocess Partners')

    partner_ids = fields.One2many('azk.partner', 'country_id', string="Partners")

    gold_count = fields.Integer(
        string="Gold Partners",
        compute="_compute_partner_counts",
        store=True
    )
    silver_count = fields.Integer(
        string="Silver Partners",
        compute="_compute_partner_counts",
        store=True
    )
    ready_count = fields.Integer(
        string="Ready Partners",
        compute="_compute_partner_counts",
        store=True
    )

    first_seen_years = fields.Char(
        string="First Seen Years",
        compute="_compute_first_seen_years"
    )

    @api.depends('partner_ids.current_status')
    def _compute_partner_counts(self):
        for country in self:
            partners = country.partner_ids
            country.total_partner_count = len(partners)
            country.gold_count = len(partners.filtered(lambda p: p.current_status == 'gold'))
            country.silver_count = len(partners.filtered(lambda p: p.current_status == 'silver'))
            country.ready_count = len(partners.filtered(lambda p: p.current_status == 'ready'))

    def _compute_first_seen_years(self):
        for country in self:
            years = country.partner_ids.mapped("first_seen_on")
            years = [str(d.year) for d in years if d]
            country.first_seen_years = ", ".join(sorted(set(years)))
