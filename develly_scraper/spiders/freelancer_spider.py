import scrapy
from urllib.parse import urljoin, urlencode
from datetime import datetime
from scrapy.http import HtmlResponse
import json
import os
import random

class FreelancerSpider(scrapy.Spider):
    name = 'freelancer'
    allowed_domains = ['freelancer.com']

    def __init__(self, country=None, category=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define root path
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Load filter mappings
        filter_path = os.path.join(self.project_root, 'common', 'filter_mapping.json')
        with open(filter_path, 'r', encoding='utf-8') as f:
            self.filter_mapping = json.load(f)
            
        # Load countries data
        countries_path = os.path.join(self.project_root, 'common', 'countries.json')
        with open(countries_path, 'r', encoding='utf-8') as f:
            self.countries = json.load(f)
            
        # Load sources data
        sources_path = os.path.join(self.project_root, 'common', 'sources.json')
        with open(sources_path, 'r', encoding='utf-8') as f:
            self.sources = json.load(f)
            
        # Find source ID for Freelancer
        self.source_id = next((source['_id'] for source in self.sources 
                             if source['name'] == 'Freelancer'), '607f1f77bcf86cd799439001')
        
        # Set up country list and mapping
        self.location_codes = []
        self.location_info = {}
        
        # Build location codes and info
        for country_data in self.countries:
            self.location_codes.append(country_data['code'])
            self.location_info[country_data['code']] = {
                'country_id': country_data['_id'],
                'country_name': country_data['name']
            }
            
        # If specific country provided, use only that one
        if country:
            if country.upper() in self.location_codes:
                self.location_codes = [country.upper()]
            else:
                self.logger.warning(f"Country code {country} not found in countries.json. Using all countries.")
        else:
            # Default to top countries for development
            self.location_codes = ['FR', 'GB', 'US', 'DE', 'IN']
            # Shuffle the location codes for random starting point
            random.shuffle(self.location_codes)
            self.logger.info(f"Shuffled location codes, starting with: {self.location_codes[0]}")
        
        # Set up country slug mapping for URLs
        self.country_map = {}
        for country_data in self.countries:
            country_name = country_data['name'].lower().replace(' ', '-')
            self.country_map[country_data['code']] = country_name
        
        # Get categories from filter mapping
        self.categories = []
        self.category_info = {}
        
        # If filter mapping for Freelancer exists, use it
        # For now, use default categories if not in mapping
        if 'Freelancer' not in self.filter_mapping:
            self.categories = ["website-design", "wordpress", "php", "javascript", "logo-design"]
            for cat in self.categories:
                self.category_info[cat] = {
                    'main_category': 'Development',
                    'subcategory': cat.replace('-', ' ').title(),
                    'category_id': self.categories.index(cat) + 1
                }
        else:
            for main_category, subcategories in self.filter_mapping.get('Freelancer', {}).items():
                for subcategory_name, category_id in subcategories.items():
                    skill_name = subcategory_name.lower().replace(' ', '-')
                    self.categories.append(skill_name)
                    self.category_info[skill_name] = {
                        'main_category': main_category,
                        'subcategory': subcategory_name,
                        'category_id': category_id
                    }
                    
        # Override categories if specified
        if category:
            category = category.lower().replace(' ', '-')
            if category in self.categories:
                self.categories = [category]
            else:
                self.categories = [category]
                self.category_info[category] = {
                    'main_category': 'Other',
                    'subcategory': category.replace('-', ' ').title(),
                    'category_id': '999'
                }
        else:
            # Shuffle the categories for random starting point
            random.shuffle(self.categories)
            self.logger.info(f"Shuffled categories, starting with: {self.categories[0]}")
        
        self.logger.info(f"Initialized with {len(self.categories)} categories and {len(self.location_codes)} countries")
        self.logger.info(f"Categories: {self.categories}")
        self.logger.info(f"Countries: {self.location_codes}")
        
        # Set up output directory
        os.makedirs("output", exist_ok=True)
        self.output_file = f"output/freelancer_all.json"

    def start_requests(self):
        """Start with the first category and location"""
        if self.categories and self.location_codes:
            first_category = self.categories[0]
            first_location = self.location_codes[0]
            
            category_data = self.category_info.get(first_category, {})
            location_data = self.location_info.get(first_location, {})
            
            # Determine URL based on country and category
            country_slug = self.country_map.get(first_location)
            
            if country_slug:
                url = f"https://www.freelancer.com/freelancers/{country_slug}/{first_category}"
            else:
                url = f"https://www.freelancer.com/freelancers/skills/{first_category}"
                
            self.logger.info(f"Starting with URL: {url}")
            self.logger.info(f"Category: {first_category} ({category_data.get('main_category', '')}: {category_data.get('subcategory', '')})")
            self.logger.info(f"Location: {first_location} ({location_data.get('country_name', '')})")
            
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [{"method": "wait_for_timeout", "args": [3000]}],
                    "category": first_category,
                    "category_data": category_data,
                    "location": first_location,
                    "location_data": location_data,
                    "page": 1
                }
            )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            self.logger.error("❌ La réponse n'est pas de type HtmlResponse.")
            return

        # Get current category, location and page from meta
        current_category = response.meta.get("category")
        category_data = response.meta.get("category_data", {})
        current_location = response.meta.get("location")
        location_data = response.meta.get("location_data", {})
        current_page = response.meta.get("page", 1)
        
        self.logger.info(f"Processing category: {current_category} ({category_data.get('main_category', '')}), "
                       f"location: {current_location} ({location_data.get('country_name', '')}), page: {current_page}")

        freelancers = response.xpath('//li[contains(@class, "ns_result")]')
        self.logger.info(f"Found {len(freelancers)} freelancers on this page")
        
        for freelancer in freelancers:
            profile_href = freelancer.xpath('.//a[contains(@class,"freelancer-profile-wrapper")]/@href').get()
            profile_url = urljoin(response.url, profile_href)
            name = freelancer.xpath('.//a[contains(@class, "find-freelancer-username")]/text()').get()
            country = freelancer.xpath('.//div[@class="user-location"]/text()').get()
            thumbnail = freelancer.xpath('.//img[contains(@class, "ImageThumbnail-image")]/@src').get()
            title = freelancer.xpath('.//div[@class="user-tagline"]/text()').get()
            description = freelancer.xpath('.//div[@class="bio cleanProfile"]//span[@class="profile_text"]/text()').get()
            rating = freelancer.xpath('.//span[@class="Rating-review"]/text()').re_first(r'(\d+(\.\d+)?)')
            reviews_count = freelancer.xpath('.//span[@class="Rating-review"]//text()').re_first(r'(\d+) review')
            hourly_rate = freelancer.xpath('.//span[contains(@class, "freelancer-hourlyrate")]/@data-hourlyrate').get()
            skills = freelancer.xpath('.//div[@class="top-skills"]/a/text()').getall()

            item = {
                "url": profile_url,
                "url_of_search": response.url,
                "name": name,
                "country_id": location_data.get('country_id'),
                "country_name": location_data.get('country_name'),
                "thumbnail": thumbnail,
                "title": title,
                "description": description,
                "rating": float(rating) if rating else None,
                "reviews_count": int(reviews_count) if reviews_count else None,
                "hourly_rate": float(hourly_rate) if hourly_rate else None,
                "skills": [s.strip() for s in skills] if skills else [],
                "source": "Freelancer",
                "source_id": self.source_id,
                "main_skill": current_category,
                "created_at": datetime.utcnow().isoformat(),
                "is_verified": True,
                "category_id": category_data.get('category_id'),
                "main_category": category_data.get('main_category'),
                "subcategory": category_data.get('subcategory')
            }

            yield scrapy.Request(
                url=profile_url,
                callback=self.parse_profile,
                meta={
                    "item": item, 
                    "playwright": True,
                    "playwright_page_methods": [{"method": "wait_for_timeout", "args": [3000]}]
                }
            )

        # Check for next page in the current category and location
        if freelancers:
            # Move to the next page for the current category and location
            next_page = current_page + 1
            
            # Determine URL based on country and category 
            country_slug = self.country_map.get(current_location)
            
            if country_slug:
                next_url = f"https://www.freelancer.com/freelancers/{country_slug}/{current_category}/{next_page}"
            else:
                next_url = f"https://www.freelancer.com/freelancers/skills/{current_category}/{next_page}"
            
            self.logger.info(f"Moving to next page: {next_url}")
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [{"method": "wait_for_timeout", "args": [3000]}],
                    "category": current_category,
                    "category_data": category_data,
                    "location": current_location,
                    "location_data": location_data,
                    "page": next_page
                }
            )
        else:
            # No freelancers found, move to next location or category
            self.logger.info(f"No freelancers found for {current_category}/{current_location}, moving to next")
            yield from self._move_to_next_location_or_category(response)
                
    def _move_to_next_location_or_category(self, response):
        """Helper method to move to the next location or category"""
        current_category = response.meta.get("category")
        category_data = response.meta.get("category_data", {})
        current_location = response.meta.get("location")
        location_data = response.meta.get("location_data", {})
        
        # Find indices of current category and location
        try:
            category_index = self.categories.index(current_category)
            location_index = self.location_codes.index(current_location)
            
            # Try moving to the next location first
            if location_index < len(self.location_codes) - 1:
                # Move to next location with the same category
                next_location = self.location_codes[location_index + 1]
                next_location_data = self.location_info.get(next_location, {})
                
                self.logger.info(f"Moving to next location: {next_location} ({next_location_data.get('country_name', '')}) for category {current_category}")
                
                # Determine URL based on country and category
                country_slug = self.country_map.get(next_location)
                
                if country_slug:
                    next_url = f"https://www.freelancer.com/freelancers/{country_slug}/{current_category}"
                else:
                    next_url = f"https://www.freelancer.com/freelancers/skills/{current_category}"
                
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [{"method": "wait_for_timeout", "args": [3000]}],
                        "category": current_category,
                        "category_data": category_data,
                        "location": next_location,
                        "location_data": next_location_data,
                        "page": 1
                    }
                )
            # If we've gone through all locations, move to the next category
            elif category_index < len(self.categories) - 1:
                next_category = self.categories[category_index + 1]
                next_category_data = self.category_info.get(next_category, {})
                
                # Reset location to the first one
                first_location = self.location_codes[0]
                first_location_data = self.location_info.get(first_location, {})
                
                self.logger.info(f"Moving to next category: {next_category} ({next_category_data.get('main_category', '')}: {next_category_data.get('subcategory', '')}) with location {first_location}")
                
                # Determine URL based on country and category
                country_slug = self.country_map.get(first_location)
                
                if country_slug:
                    next_url = f"https://www.freelancer.com/freelancers/{country_slug}/{next_category}"
                else:
                    next_url = f"https://www.freelancer.com/freelancers/skills/{next_category}"
                
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [{"method": "wait_for_timeout", "args": [3000]}],
                        "category": next_category,
                        "category_data": next_category_data,
                        "location": first_location,
                        "location_data": first_location_data,
                        "page": 1
                    }
                )
            else:
                self.logger.info("All categories and locations have been processed")
        except ValueError:
            self.logger.warning(f"Category {current_category} or location {current_location} not found in the lists")

    def parse_profile(self, response):
        item = response.meta["item"]

        # Mise à jour des informations de base
        item['name'] = response.xpath('//h3[contains(@class, "Username-displayName")]/text()').get() or item['name']
        item['title'] = response.xpath('//app-user-profile-summary-tagline-redesign//h2/text()').get() or item['title']
        item['description'] = response.xpath('//app-user-profile-summary-description-redesign//fl-text//div/text()').get() or item['description']
        item['rating'] = float(response.xpath('//fl-rating/@aria-label').re_first(r'Rating: ([\d.]+)') or 0) or item['rating']
        item['reviews_count'] = int(response.xpath('//fl-review-count//div[contains(@class,"NativeElement")]/text()').re_first(r'(\d+)') or 0) or item['reviews_count']
        item['hourly_rate'] = float(response.xpath('//div[contains(@class,"HourlyRate")]//div/text()').re_first(r'\$(\d+)') or 0) or item['hourly_rate']
        item['is_verified'] = bool(response.xpath('//fl-badge[contains(@mattooltip, "Verified Freelancer")]'))
        
        # Update skills if needed
        skill_elements = response.xpath('//app-user-profile-summary-skill-list-redesign//div[@class="SkillsList"]/fl-bit//div/text()').getall()
        if skill_elements:
            item['skills'] = [s.strip() for s in skill_elements]
        
        # Compléter avec les champs manquants selon le modèle
        item['pictures'] = []
        item['min_price'] = None
        item['max_price'] = None

        # Get portfolio items
        portfolio_items = response.xpath('//app-portfolio-item')
        for portfolio in portfolio_items:
            image_url = portfolio.xpath('.//img[contains(@class, "ProjectImage")]/@src').get()
            if image_url:
                item['pictures'].append(image_url)

        # Standardiser les données selon le modèle Freelancer
        freelancer_item = {
            '_type': 'freelancer',
            'url': item['url'],
            'url_of_search': item['url_of_search'],
            'name': item['name'],
            'title': item['title'],
            'description': item['description'],
            'thumbnail': item['thumbnail'],
            'skills': item['skills'],
            'rating': item['rating'],
            'reviews_count': item['reviews_count'],
            'hourly_rate': item['hourly_rate'],
            'min_price': item['min_price'],
            'max_price': item['max_price'],
            'country_id': item['country_id'],
            'country_name': item['country_name'],
            'pictures': item['pictures'],
            'source': item['source'],
            'source_id': item['source_id'],
            'main_skill': item['main_skill'],
            'created_at': item['created_at'],
            'is_verified': item['is_verified'],
            'category_id': item.get('category_id'),
            'main_category': item.get('main_category'),
            'subcategory': item.get('subcategory')
        }

        # Enregistrement du freelancer
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(freelancer_item, ensure_ascii=False) + "\n")

        # Extraire et traiter les reviews comme des entités distinctes
        review_blocks = response.xpath('//fl-review-card')
        for review in review_blocks:
            author = review.xpath('.//div[contains(@class, "InfoContainer")]//fl-text[1]//div/text()').get()
            rating_value = review.xpath('.//fl-rating/@aria-label').re_first(r'Rating: ([\d.]+)')
            text = review.xpath('.//fl-text[position()>1 and not(ancestor::fl-link)]//div/text()').get()
            picture = review.xpath('.//fl-user-avatar//img/@src').get()
            date = review.xpath('.//fl-relative-time/span/text()').get()

            # Créer un item Review standardisé selon le modèle
            review_item = {
                '_type': 'review',
                'freelancer_id': item['url'],
                'author': author,
                'rating': float(rating_value) if rating_value else None,
                'picture': picture,
                'text': text,
                'title': None,
                'created_at': date or datetime.utcnow().isoformat(),
                'source': item['source'],
                'source_id': item['source_id'],
                'category_id': item.get('category_id'),
                'main_category': item.get('main_category'),
                'subcategory': item.get('subcategory')
            }

            # Enregistrement de la review
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(review_item, ensure_ascii=False) + "\n")
            
            yield review_item

        yield freelancer_item
