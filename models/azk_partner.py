from odoo import models, fields, api
import requests
import logging
from bs4 import BeautifulSoup
from datetime import date
import time

_logger = logging.getLogger(__name__)

class AzkPartner(models.Model):
    _name = 'azk.partner'
    _description = 'Odoo Partner Information'

    name = fields.Char(string='Partner Name', required=True)
    partner_url = fields.Char(string='Partner URL')
    current_status = fields.Selection(
        selection=[('gold', 'Gold'), ('silver', 'Silver'), ('ready', 'Ready')],
        string='Current Status'
    )
    country_id = fields.Many2one('res.country', string='Country')
    first_seen_on = fields.Date(string='First Seen On')
    retention_rate = fields.Float(string='Retention Rate')
    total_references_count = fields.Integer(string='Total References Count')
    largest_project_size = fields.Integer(string='Largest Project Size')
    average_project_size = fields.Float(string='Average Project Size')
    to_reprocess_references = fields.Boolean(string='To Reprocess References')
    status_history_ids = fields.One2many('partner.status.history', 'partner_id', string='Status History')
    reference_ids = fields.One2many('partner.reference', 'partner_id', string='References')

    def scrape_partners_lebanon(self):
        url = "https://www.odoo.com/partners/country/lebanon-122"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            _logger.info(f"Fetching partners from: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            _logger.info(f"Successfully fetched page. Status: {response.status_code}")
            
        except requests.RequestException as e:
            _logger.error(f"Failed to fetch partners page: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        
        with open("/tmp/odoo_partners_debug.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        _logger.info("Saved HTML to /tmp/odoo_partners_debug.html for inspection")

        possible_selectors = [
            ".o_partner_card",
            ".partner-card",
            ".card", 
            ".partner_item",
            "[class*='partner']",
            ".col-md-4",  
            ".mb-4" 
        ]

        partners = []
        
        for selector in possible_selectors:
            cards = soup.select(selector)
            _logger.info(f"🔍 Trying selector '{selector}': found {len(cards)} elements")
            
            if cards:
                _logger.info(f"Using selector: {selector}")
                break

        if not cards:
            _logger.warning("No partner cards found with any selector")
            all_links = soup.find_all('a', href=True)
            partner_links = [link for link in all_links if '/partners/' in link['href']]
            _logger.info(f"Found {len(partner_links)} potential partner links")
            return []

        for i, card in enumerate(cards):
            _logger.info(f"Processing card {i+1}/{len(cards)}")
            
            try:
                name = None
                name_selectors = ["h3 a", "h2 a", "h3", "h2", ".partner-name", "a h3", "a h2"]
                
                for name_selector in name_selectors:
                    name_tag = card.select_one(name_selector)
                    if name_tag:
                        name = name_tag.get_text(strip=True)
                        if name:
                            break
                
                partner_url = None
                url_selectors = ["h3 a", "h2 a", "a"]
                
                for url_selector in url_selectors:
                    url_tag = card.select_one(url_selector)
                    if url_tag and url_tag.get('href'):
                        href = url_tag['href']
                        if href.startswith('/'):
                            partner_url = f"https://www.odoo.com{href}"
                        else:
                            partner_url = href
                        break

                status = None
                status_selectors = [".level", ".badge", ".status", ".partner-level", "[class*='level']"]
                
                for status_selector in status_selectors:
                    status_tag = card.select_one(status_selector)
                    if status_tag:
                        status = status_tag.get_text(strip=True)
                        if status:
                            break

                if name:
                    partner_data = {
                        "name": name,
                        "url": partner_url,
                        "status": status,
                    }
                    partners.append(partner_data)
                    _logger.info(f"Found partner: {name} | Status: {status} | URL: {partner_url}")
                else:
                    _logger.warning(f"Could not extract name from card {i+1}")

            except Exception as e:
                _logger.error(f"Error processing card {i+1}: {e}")
                continue

        _logger.info(f"Total partners found: {len(partners)}")
        
        self._create_or_update_partners(partners)
        
        return partners

    def _create_or_update_partners(self, partners_data):
        """Create or update partner records in Odoo"""
        country_lebanon = self.env['res.country'].search([('name', '=', 'Lebanon')], limit=1)
        
        if not country_lebanon:
            _logger.warning("Lebanon country not found in Odoo database")
        
        for partner_data in partners_data:
            try:
                status_mapping = {
                    'gold': 'gold',
                    'silver': 'silver', 
                    'ready': 'ready'
                }
                
                status_key = partner_data.get('status', '').lower()
                current_status = status_mapping.get(status_key, 'ready')
                
                existing_partner = self.search([
                    ('name', '=', partner_data['name'])
                ], limit=1)
                
                if existing_partner:
                    existing_partner.write({
                        'partner_url': partner_data['url'],
                        'current_status': current_status,
                        'country_id': country_lebanon.id,
                    })
                    _logger.info(f"🔄 Updated partner: {partner_data['name']}")
                else:
                    self.create({
                        'name': partner_data['name'],
                        'partner_url': partner_data['url'],
                        'current_status': current_status,
                        'country_id': country_lebanon.id,
                        'first_seen_on': date.today(),
                    })
                    _logger.info(f"Created new partner: {partner_data['name']}")
                    
            except Exception as e:
                _logger.error(f"Error creating/updating partner {partner_data.get('name')}: {e}")

    def test_scraping(self):
        """Test method to run scraping manually"""
        _logger.info("Starting test scraping...")
        results = self.scrape_partners_lebanon()
        _logger.info(f"Test completed. Found {len(results)} partners.")
        return True