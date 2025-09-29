{
    'name': 'Azk Odoo Partner Monitor',
    'version': '18.0',
    'description': 'scrape partner data from the official Odoo Partners page',
    'summary': 'scrape partner data from the official Odoo Partners page, store this information, track historical changes, and provide analytical views and dashboards for reporting, all within the Odoo environment',
    'author': 'fayrouz',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['mail','base',],
    'data': [
        'data/cron_partners.xml',
        'security/ir.model.access.csv',
        'views/azk_partner.xml',
        'views/partner_country.xml',
    ],
}