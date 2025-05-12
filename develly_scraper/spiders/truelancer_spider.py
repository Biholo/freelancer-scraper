import scrapy
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from datetime import datetime
from scrapy.http import HtmlResponse
import json
import os
import random
from develly_scraper.items import FreelancerItem, ReviewItem

class TruelancerSpider(scrapy.Spider):
    name = 'truelancer'
    allowed_domains = ['truelancer.com']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country_code = kwargs.get('country', 'ALL').upper()
        
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
            
        # Find source ID for TrueLancer
        self.source_id = next((source['_id'] for source in self.sources 
                               if source['name'] == 'TrueLancer'), '607f1f77bcf86cd799439003')
        
        # Set up country list
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
        if self.country_code != 'ALL':
            if self.country_code in self.location_codes:
                self.location_codes = [self.country_code]
            else:
                self.logger.warning(f"Country code {self.country_code} not found in countries.json. Using all countries.")
                self.location_codes = ['FR', 'GB', 'US', 'DE', 'IN']  # Default to top countries for development
                # Shuffle the location codes for random starting point
                random.shuffle(self.location_codes)
                self.logger.info(f"Shuffled location codes, starting with: {self.location_codes[0]}")
        else:
            # Default to top countries for development
            self.location_codes = ['FR', 'GB', 'US', 'DE', 'IN']
            # Shuffle the location codes for random starting point
            random.shuffle(self.location_codes)
            self.logger.info(f"Shuffled location codes, starting with: {self.location_codes[0]}")
        
        # Get categories from filter mapping
        self.categories = []
        self.category_names = {}
        
        for main_category, subcategories in self.filter_mapping.get('Truelancer', {}).items():
            for subcategory_name, category_id in subcategories.items():
                self.categories.append(category_id)
                self.category_names[category_id] = {
                    'main_category': main_category,
                    'subcategory': subcategory_name
                }
        
        # Shuffle the categories for random starting point
        random.shuffle(self.categories)
        self.logger.info(f"Shuffled categories, starting with: {self.categories[0]}")
                
        self.logger.info(f"Loaded {len(self.categories)} categories from filter mapping")
        self.logger.info(f"Categories: {self.category_names}")
        self.logger.info(f"Countries: {self.location_codes}")
        
        # Set up output directory (for JSON exports if needed)
        os.makedirs('output', exist_ok=True)
        
        # Debug: Print settings to verify MongoDB configuration
        from scrapy.utils.project import get_project_settings
        settings = get_project_settings()
        self.logger.info(f"MongoDB URI: {settings.get('MONGO_URI')}")
        self.logger.info(f"MongoDB Database: {settings.get('MONGO_DATABASE')}")
        self.logger.info(f"Item Pipelines: {settings.get('ITEM_PIPELINES')}")
        
    def start_requests(self):
        """Start with the first category and location"""
        if self.categories and self.location_codes:
            # Start with the first category and first location
            first_category = self.categories[0]
            first_location = self.location_codes[0]
            
            url = f'https://www.truelancer.com/freelancers?page=1&slist={first_category}'
            if first_location != 'ALL':
                url = f"{url}&clist={first_location}"
                
            self.logger.info(f"Starting with URL: {url}")
            self.logger.info(f"Category: {first_category} ({self.category_names.get(first_category, {}).get('main_category', '')}: {self.category_names.get(first_category, {}).get('subcategory', '')})")
            self.logger.info(f"Location: {first_location} ({self.location_info.get(first_location, {}).get('country_name', '')})")
            
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [{"method": "wait_for_timeout", "args": [5000]}],
                    "category_id": first_category,
                    "category_info": self.category_names.get(first_category, {}),
                    "location": first_location,
                    "location_data": self.location_info.get(first_location, {})
                }
            )

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            self.logger.error("❌ La réponse n'est pas de type HtmlResponse.")
            return

        current_category = response.meta.get("category_id")
        category_info = response.meta.get("category_info", {})
        current_location = response.meta.get("location")
        location_data = response.meta.get("location_data", {})
        
        self.logger.info(f"Processing category: {current_category} ({category_info.get('main_category', '')}: {category_info.get('subcategory', '')}), "
                       f"location: {current_location} ({location_data.get('country_name', '')}), page: {self._get_page_number(response.url)}")
        
        freelancers = response.xpath('//div[starts-with(@id, "user-")]')
        self.logger.info(f"Found {len(freelancers)} freelancers on this page")

        for freelancer in freelancers:
            profile_url = freelancer.xpath('.//h3/a/@href').get()
            if not profile_url:
                continue
                
            full_url = urljoin(response.url, profile_url)

            # Get country from freelancer profile
            country_name = freelancer.xpath('.//p[contains(@class, "fl_location")]//img/@title').get()
            country_id = None
            if country_name:
                country_match = next((country for country in self.countries 
                                     if country['name'] == country_name), None)
                if country_match:
                    country_id = country_match['_id']

            # Extraction sécurisée des données
            hourly_rate_text = freelancer.xpath('.//p[contains(text(), "$")]/text()').re_first(r'(\d+)')
            try:
                hourly_rate = float(hourly_rate_text) if hourly_rate_text else None
            except (ValueError, TypeError):
                hourly_rate = None
                
            rating_value = len(freelancer.xpath('.//span[contains(@class, "MuiRating-iconFilled")]'))
            
            reviews_count_text = freelancer.xpath('.//p/span[contains(text(), "project")]/text()').re_first(r'(\d+)')
            try:
                reviews_count = int(reviews_count_text) if reviews_count_text else None
            except (ValueError, TypeError):
                reviews_count = None

            item = {
                'name': freelancer.xpath('.//h3/a/text()').get(),
                'url': full_url,
                'thumbnail': freelancer.xpath('.//img[contains(@alt, "-Freelancer")]/@src').get(),
                'country_id': country_id,
                'country_name': country_name,
                'title': freelancer.xpath('.//p[contains(@class, "fontBold")]/text()').get(),
                'description': freelancer.xpath('.//p[contains(@class, "textLabel")]/text()').get(),
                'hourly_rate': hourly_rate,
                'rating': rating_value,
                'reviews_count': reviews_count,
                'source': 'TrueLancer',
                'source_id': self.source_id,
                'url_of_search': response.url,
                'created_at': datetime.utcnow().isoformat(),
                'category_id': current_category,
                'main_category': category_info.get('main_category'),
                'subcategory': category_info.get('subcategory'),
                'current_location': current_location,
                'location_data': location_data
            }

            yield scrapy.Request(
                full_url,
                callback=self.parse_profile,
                meta={
                    'item': item,
                    "playwright": True,
                    "playwright_page_methods": [{"method": "wait_for_timeout", "args": [5000]}]
                }
            )

        # Check for next page in the current category and location
        next_page = response.xpath('//a[contains(text(), "Next")]/@href').get()
        if next_page:
            self.logger.info(f"Moving to next page in category {current_category}, location {current_location}")
            yield response.follow(
                next_page,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [{"method": "wait_for_timeout", "args": [5000]}],
                    "category_id": current_category,
                    "category_info": category_info,
                    "location": current_location,
                    "location_data": location_data
                }
            )
        else:
            # Move to the next location or category
            yield from self._move_to_next_location_or_category(response)

    def _move_to_next_location_or_category(self, response):
        """Helper method to move to the next location or category"""
        current_category = response.meta.get("category_id")
        category_info = response.meta.get("category_info", {})
        current_location = response.meta.get("location")
        location_data = response.meta.get("location_data", {})
        
        # Find indices
        try:
            category_index = self.categories.index(current_category)
            location_index = self.location_codes.index(current_location)
            
            # Try moving to the next location first
            if location_index < len(self.location_codes) - 1:
                next_location = self.location_codes[location_index + 1]
                next_location_data = self.location_info.get(next_location, {})
                
                self.logger.info(f"Moving to next location: {next_location} ({next_location_data.get('country_name', '')}) for category {current_category}")
                
                url = f'https://www.truelancer.com/freelancers?page=1&slist={current_category}'
                if next_location != 'ALL':
                    url = f"{url}&clist={next_location}"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [{"method": "wait_for_timeout", "args": [5000]}],
                        "category_id": current_category,
                        "category_info": category_info,
                        "location": next_location,
                        "location_data": next_location_data
                    }
                )
            # If we've gone through all locations, move to the next category
            elif category_index < len(self.categories) - 1:
                next_category = self.categories[category_index + 1]
                next_category_info = self.category_names.get(next_category, {})
                
                # Reset location to the first one
                first_location = self.location_codes[0]
                first_location_data = self.location_info.get(first_location, {})
                
                self.logger.info(f"Moving to next category: {next_category} ({next_category_info.get('main_category', '')}: {next_category_info.get('subcategory', '')}) with location {first_location}")
                
                url = f'https://www.truelancer.com/freelancers?page=1&slist={next_category}'
                if first_location != 'ALL':
                    url = f"{url}&clist={first_location}"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [{"method": "wait_for_timeout", "args": [5000]}],
                        "category_id": next_category,
                        "category_info": next_category_info,
                        "location": first_location,
                        "location_data": first_location_data
                    }
                )
            else:
                self.logger.info("All categories and locations have been processed")
        except ValueError as e:
            self.logger.warning(f"Error finding category or location index: {e}")
            
            # Récupération en cas d'erreur: commencer avec la première catégorie et le premier pays
            if self.categories and self.location_codes:
                first_category = self.categories[0]
                first_location = self.location_codes[0]
                first_category_info = self.category_names.get(first_category, {})
                first_location_data = self.location_info.get(first_location, {})
                
                self.logger.info(f"Recovering from error - starting with first category: {first_category} and location: {first_location}")
                
                url = f'https://www.truelancer.com/freelancers?page=1&slist={first_category}'
                if first_location != 'ALL':
                    url = f"{url}&clist={first_location}"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [{"method": "wait_for_timeout", "args": [5000]}],
                        "category_id": first_category,
                        "category_info": first_category_info,
                        "location": first_location,
                        "location_data": first_location_data
                    }
                )

    def _get_page_number(self, url):
        """Extract page number from the URL"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        return query_params.get('page', ['1'])[0]

    def parse_profile(self, response):
        try:
            item = response.meta.get('item', {})
            if not item:
                self.logger.error("Item data missing in meta")
                return

            # Extraction sécurisée des données avec gestion des valeurs nulles
            description = response.xpath(
                '//div[@id="overview"]//p[contains(@class,"MuiTypography-body1") and not(@class="textLabel")]/text()'
            ).get()
            
            item['description'] = item.get('description') or description
            
            # Extraction des compétences de manière sécurisée
            skills = response.xpath(
                '//div[contains(@class, "fl_skills")]//span/text()'
            ).getall()
            
            if not skills:
                skills = response.xpath(
                    '//div[@id="overview"]/following::div[.//text()="My Expertise"]//span/text()'
                ).getall()
                
            item['skills'] = skills or []
            
            # Extraction des images du portfolio
            pictures = response.xpath(
                '//img[contains(@src, "cdn.truelancer.com/project-pictures")]/@src'
            ).getall() or []
            
            item['pictures'] = pictures
            
            # Extraction et conversion sécurisée de la note
            # La notation est dans une div avec la classe 'total-rating'
            rating_text = response.xpath('//div[contains(@class, "total-rating")]/text()').get()
            if not rating_text:
                # Essayons de trouver dans les éléments de classe rating avec des étoiles actives
                stars_count = len(response.xpath('//ul[contains(@class, "rating")]//li/a/span[contains(@class, "active")]'))
                if stars_count > 0:
                    rating_text = str(stars_count)
            
            try:
                rating = float(rating_text) if rating_text else (item.get('rating') or None)
            except (ValueError, TypeError):
                rating = item.get('rating') or None
                
            item['rating'] = rating
            
            # Extraction et conversion sécurisée du nombre d'avis
            # Le nombre d'avis est généralement dans une div avec la classe 'total-reviews' 
            # avec le format (XX) où XX est le nombre d'avis
            reviews_count_text = response.xpath('//div[contains(@class, "total-reviews")]/text()').re_first(r'\((\d+)\)')
            
            # Si pas trouvé, chercher dans d'autres endroits possibles
            if not reviews_count_text:
                # Vérifier dans la section des insights
                reviews_count_text = response.xpath('//div[contains(@class, "memberStats-item")]//div[contains(@class, "insights-label") and contains(text(), "Projects")]/following-sibling::div[contains(@class, "insights-value")]/text()').get()
                if reviews_count_text:
                    reviews_count_text = reviews_count_text.strip()
            
            # Si toujours pas trouvé, essayer dans les onglets de portfolio/avis
            if not reviews_count_text:
                reviews_count_text = response.xpath('//a[@role="tab" and contains(text(), "Portfolio")]').re_first(r'\((\d+)\)')
            
            # Dernière tentative: compter les éléments d'avis directement
            if not reviews_count_text:
                reviews_elements = response.xpath('//li[contains(@class, "item participant feedback")]')
                if reviews_elements:
                    reviews_count_text = str(len(reviews_elements))
                    
            try:
                reviews_count = int(reviews_count_text) if reviews_count_text else (item.get('reviews_count') or None)
            except (ValueError, TypeError):
                reviews_count = item.get('reviews_count') or None
                
            item['reviews_count'] = reviews_count
            
            # Extraction de la compétence principale
            item['main_skill'] = item['skills'][0] if item.get('skills') and len(item.get('skills', [])) > 0 else None
            
            # Vérification du statut de vérification
            item['is_verified'] = "verified" in response.text.lower() if response.text else False

            # Education - gestion sécurisée
            education = response.xpath('//div[@id="education"]//div[contains(@class, "mui-e33hax")]')
            item['education'] = []
            
            for edu in education:
                education_item = {
                    "institution": edu.xpath('./div/p[1]/text()').get() or "",
                    "degree": edu.xpath('./p[1]/text()').get() or "",
                    "period": edu.xpath('./p[2]/text()').get() or ""
                }
                item['education'].append(education_item)

            # Experience - gestion sécurisée
            experience = response.xpath('//div[@id="experience"]//div[contains(@class, "mui-e33hax")]')
            item['experience'] = []
            
            for xp in experience:
                experience_item = {
                    "title": xp.xpath('./p[1]/text()').get() or "",
                    "company": xp.xpath('./p[2]/text()').get() or "",
                    "period": xp.xpath('./p[3]/text()').get() or "",
                    "location": xp.xpath('./p[4]/text()').get() or ""
                }
                item['experience'].append(experience_item)

            # Compléter avec les champs manquants selon le modèle
            item['min_price'] = None
            item['max_price'] = None
            
            # Conversion des types de données avec gestion d'erreurs
            try:
                item['hourly_rate'] = float(item['hourly_rate']) if item.get('hourly_rate') else None
            except (ValueError, TypeError):
                item['hourly_rate'] = None
                
            try:
                item['rating'] = float(item['rating']) if item.get('rating') else None
            except (ValueError, TypeError):
                item['rating'] = None
                
            try:
                item['reviews_count'] = int(item['reviews_count']) if item.get('reviews_count') else None
            except (ValueError, TypeError):
                item['reviews_count'] = None

            # Create a dictionary for MongoDB instead of using FreelancerItem
            freelancer_dict = {
                '_type': 'freelancer',  # Add type for MongoDB collection determination
                'url': item.get('url', ''),
                'url_of_search': item.get('url_of_search', ''),
                'name': item.get('name', ''),
                'title': item.get('title', ''),
                'description': item.get('description', ''),
                'thumbnail': item.get('thumbnail', ''),
                'skills': item.get('skills', []),
                'rating': item.get('rating'),
                'reviews_count': item.get('reviews_count'),
                'hourly_rate': item.get('hourly_rate'),
                'min_price': item.get('min_price'),
                'max_price': item.get('max_price'),
                'country_id': item.get('country_id'),
                'country_name': item.get('country_name', ''),
                'pictures': item.get('pictures', []),
                'source': item.get('source', 'TrueLancer'),
                'source_id': item.get('source_id'),
                'main_skill': item.get('main_skill'),
                'created_at': item.get('created_at', datetime.utcnow().isoformat()),
                'is_verified': item.get('is_verified', False)
            }

            # Debug: Print what we're yielding
            self.logger.info(f"YIELDING FREELANCER: {freelancer_dict.get('name', 'unknown')} - {freelancer_dict.get('url', 'no-url')}")
            
            # Use MongoDB pipeline
            yield freelancer_dict

            # Extraire et traiter les reviews comme des entités distinctes
            review_blocks = response.xpath('//div[@id="reviews"]//div[contains(@class, "feedbackItemContainer")]')
            
            for review in review_blocks:
                try:
                    # Extraction sécurisée des données de l'avis
                    author = review.xpath('.//img/@alt').get() or 'Unknown'
                    
                    try:
                        rating_value = float(len(review.xpath('.//span[contains(@class, "MuiRating-iconFilled")]')))
                    except (ValueError, TypeError):
                        rating_value = 0.0
                        
                    picture = review.xpath('.//img/@src').get() or ''
                    text = review.xpath('.//p[not(contains(@class, "textLabel")) and @style][1]/text()').get() or ''
                    title = review.xpath('.//p[contains(@class, "textSmall")]/text()').get() or ''
                    created_at_text = review.xpath('.//p[contains(@class, "textLabel")]/text()').re_first(r'on (.+)$')
                    created_at = created_at_text or datetime.utcnow().isoformat()
                    
                    # Créer un dictionnaire pour MongoDB au lieu d'utiliser ReviewItem
                    review_dict = {
                        '_type': 'review',
                        'freelancer_id': item.get('url', ''),
                        'author': author,
                        'rating': rating_value,
                        'picture': picture,
                        'text': text,
                        'title': title,
                        'created_at': created_at,
                        'source': item.get('source', 'TrueLancer'),
                        'source_id': item.get('source_id')
                    }
                    
                    # Debug: Print what we're yielding
                    self.logger.info(f"YIELDING REVIEW for {item.get('name', 'unknown')} by {review_dict.get('author', 'unknown')}")
                    
                    # Use MongoDB pipeline
                    yield review_dict
                    
                except Exception as e:
                    self.logger.error(f"Error processing review: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error in parse_profile: {str(e)}")
