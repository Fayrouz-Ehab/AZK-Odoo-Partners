from odoo import models, fields, api


class StatusHistory(models.Model):
    _name = 'partner.status.history'
    _description = 'Odoo Partner Status History'

    partner_id = fields.Many2one('azk.partner', string='Partner', required=True)
    previous_status = fields.Selection([
        ('prospect', 'Prospect'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended')
    ], string='Previous Status')
    new_status = fields.Selection([
        ('prospect', 'Prospect'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended')
    ], string='New Status', required=True)
    change_date = fields.Date(string='Change Date', required=True)
    change_type = fields.Selection([
        ('promoted', 'Promoted'),
        ('demoted', 'Demoted'),
        ('initial', 'Initial')
    ], string='Change Type', required=True)

   