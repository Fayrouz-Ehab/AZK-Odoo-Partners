from odoo import models, fields, api   

_logger = models.logging.getLogger(__name__)

class PartnerReference(models.Model):
    _name = 'partner.reference'
    _description = 'Odoo Partner Reference'

    partner_id = fields.Many2one('azk.partner', string='Partner', required=True)
    name = fields.Char(string='Reference Client Name', required=True)
    is_active = fields.Boolean(string='Is Active', default=True)
    added_on = fields.Date(string='Added On')
    removed_on = fields.Date(string='Removed On')


    def _sync_partner_references(self, partner, scraped_references):
        Reference = self.env['partner.reference']
        
        existing_refs = Reference.search([('partner_id', '=', partner.id), ('is_active', '=', True)])
        existing_names = set(existing_refs.mapped('name'))
        scraped_names = set(scraped_references)

        new_refs = scraped_names - existing_names
        for ref_name in new_refs:
            Reference.create({
                'partner_id': partner.id,
                'name': ref_name,
                'is_active': True,
                'added_on': fields.Date.today(),
            })
            _logger.info(f"New reference added for {partner.name}: {ref_name}")

        removed_refs = existing_names - scraped_names
        for ref in existing_refs.filtered(lambda r: r.name in removed_refs):
            ref.write({
                'is_active': False,
                'removed_on': fields.Date.today(),
            })
            _logger.info(f"Reference removed for {partner.name}: {ref.name}")

    