import scrapy
from urllib.parse import urlencode, urlparse, parse_qs
from datetime import datetime
import json
import os
import random


class PeoplePerHourSpider(scrapy.Spider):
    name = "peopleperhour"
    allowed_domains = ["peopleperhour.com"]

    def __init__(self, location=None, category=None, *args, **kwargs):
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
            
        # Find source ID for PeoplePerHour
        self.source_id = next((source['_id'] for source in self.sources 
                             if source['name'] == 'PeoplePerHour'), '607f1f77bcf86cd799439002')
                             
        # Get categories from filter mapping 
        self.categories = []
        self.category_info = {}
        
        # Build categories and mapping from filter_mapping.json
        for main_category, subcategories in self.filter_mapping.get('PeoplePerHour', {}).items():
            for subcategory_name, category_id in subcategories.items():
                # Stocker l'ID numérique tel quel
                # La clé sera 'subcategory_name-ID'
                key = f"{subcategory_name}-{category_id}"
                self.categories.append(key)
                self.category_info[key] = {
                    'main_category': main_category,
                    'subcategory': subcategory_name,
                    'category_id': category_id
                }
                
        # Override categories if specified
        if category:
            # Rechercher dans les catégories existantes
            matching_keys = [key for key in self.categories 
                            if category.lower() in key.lower()]
            if matching_keys:
                self.categories = matching_keys
            else:
                self.logger.warning(f"Category {category} not found in filter_mapping.json. Using default categories.")
        else:
            # Shuffle the categories for random starting point
            random.shuffle(self.categories)
            self.logger.info(f"Shuffled categories, starting with: {self.categories[0]}")

        # Get countries and build location mapping
        self.location_codes = []
        self.location_info = {}
        
        for country in self.countries:
            self.location_codes.append(country['code'])
            self.location_info[country['code']] = {
                'country_id': country['_id'],
                'country_name': country['name']
            }
            
        # If specific location provided, use only that one
        if location:
            if location.upper() in self.location_codes:
                self.location_codes = [location.upper()]
            else:
                self.logger.warning(f"Location code {location} not found in countries.json. Using all locations.")
        else:
            # Default to top countries for development
            self.location_codes = ['FR', 'GB', 'US', 'DE', 'IN']
            # Shuffle the location codes for random starting point
            random.shuffle(self.location_codes)
            self.logger.info(f"Shuffled location codes, starting with: {self.location_codes[0]}")
            
        self.logger.info(f"Initialized with {len(self.categories)} categories and {len(self.location_codes)} locations")
        
        # Set up output file
        os.makedirs("output", exist_ok=True)
        self.output_file = f"output/peopleperhour_{self.location_codes[0] if self.location_codes else 'ALL'}.json"

    def start_requests(self):
        """Start with the first category and location"""
        if self.categories and self.location_codes:
            first_category_key = self.categories[0]
            first_location = self.location_codes[0]
            
            # Extraire le category_id depuis les infos de catégorie
            category_data = self.category_info.get(first_category_key, {})
            category_id = category_data.get('category_id')
            
            # Utiliser le category_id numérique dans l'URL
            url = f"https://www.peopleperhour.com/hire-freelancers?{urlencode({'location': first_location, 'industries': str(category_id)})}"
            
            location_data = self.location_info.get(first_location, {})
            
            self.logger.info(f"Starting with URL: {url}")
            self.logger.info(f"Category: {category_data.get('subcategory', '')} ({category_data.get('main_category', '')}, ID: {category_id})")
            self.logger.info(f"Location: {first_location} ({location_data.get('country_name', '')})")
            
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "category_key": first_category_key,
                    "category_data": category_data,
                    "location": first_location,
                    "location_data": location_data,
                    "page": 1
                }
            )

    def parse(self, response):
        # Get current category, location and page from meta
        current_category_key = response.meta.get("category_key")
        category_data = response.meta.get("category_data", {})
        category_id = category_data.get('category_id')
        current_location = response.meta.get("location")
        location_data = response.meta.get("location_data", {})
        current_page = response.meta.get("page", 1)
        
        # Si on rencontre une page 404, passer à la catégorie/location suivante
        if response.status == 404:
            self.logger.warning(f"Page 404 pour la catégorie {category_data.get('subcategory', '')} (ID: {category_id}) et location {current_location}. Passage à la suivante.")
            return self._move_to_next_location_or_category(response)
        
        self.logger.info(f"Processing category: {category_data.get('subcategory', '')} ({category_data.get('main_category', '')}, ID: {category_id}), "
                       f"location: {current_location} ({location_data.get('country_name', '')}), page: {current_page}")
        
        # Nouvelle sélection XPath pour les cartes de freelancers sur la nouvelle structure du site
        cards = response.xpath('//div[contains(@class, "freelancer-card") or contains(@class, "FreelancerCard")]')
        
        self.logger.info(f"Found {len(cards)} freelancer cards on this page")
        
        for card in cards:
            # Extraire l'URL du profil freelancer
            profile_url = card.xpath('.//a[contains(@class, "card__title-wrapper") or contains(@href, "/freelancer/")]/@href').get()
            if profile_url:
                profile_url = response.urljoin(profile_url)

            # Extraire les informations du freelancer depuis la carte
            name = card.xpath('.//h2[contains(@class, "card__title") or contains(@class, "freelancer-name")]/text()').get('').strip()
            job_title = card.xpath('.//p[contains(@class, "card__job-title") or contains(@class, "freelancer-title")]/span/text()').get('').strip()
            
            # Extraire le pays (texte et code)
            country_name = card.xpath('.//div[contains(@class, "card__country") or contains(@class, "freelancer-country")]//span[not(contains(@class, "card__country-icon"))]/text()').get('').strip()
            country_icon_title = card.xpath('.//div[contains(@class, "card__country") or contains(@class, "freelancer-country")]//svg/title/text()').get('').strip()
            displayed_country = country_name or country_icon_title
            
            # Extraire la note et le nombre d'avis
            rating = card.xpath('.//div[contains(@class, "card__freelancer-ratings") or contains(@class, "freelancer-rating")]/a/text()').re_first(r'([\d.]+)')
            reviews_count = card.xpath('.//span[contains(@class, "card__freelancer-reviews") or contains(@class, "freelancer-reviews-count")]/text()').re_first(r'\((\d+)\)')
            
            # Extraire l'avatar
            avatar = card.xpath('.//img[contains(@class, "user-avatar") or contains(@alt, "avatar")]/@src').get()
            
            # Extraire les compétences
            skills = card.xpath('.//a[contains(@class, "Tag") or contains(@href, "/hire-freelancers")]//span[contains(@class, "Tag__label")]/text()').getall()
            
            # Extraire le prix horaire
            hourly_rate = card.xpath('.//span[contains(@class, "card__price") or contains(@class, "freelancer-price")]/span[1]/text()').re_first(r'[\d,.]+')
            if hourly_rate:
                hourly_rate = hourly_rate.replace('€', '').replace('£', '').replace('$', '').replace(',', '').strip()
            
            # Extraire le nombre de projets
            projects_count = card.xpath('.//div[contains(@class, "card__main--bottom-left") or contains(@class, "freelancer-projects")]//span/text()').re_first(r'(\d+)')

            card_data = {
                "title": job_title,
                "url": profile_url,
                "tags": skills,
                "price_eur": hourly_rate,
                "freelancer_name": name,
                "freelancer_url": profile_url,
                "freelancer_rating": rating,
                "freelancer_reviews": reviews_count,
                "freelancer_avatar": avatar,
                "displayed_country": displayed_country,
                "projects_count": projects_count,
                "category": current_category_key,
                "category_data": category_data,
                "location": current_location,
                "location_data": location_data,
                "source_id": self.source_id
            }

            # Suivre l'URL du profil pour obtenir plus de détails
            if profile_url:
                yield response.follow(profile_url, callback=self.parse_detail, meta={"card_data": card_data})

        # Check for more results on the page
        if cards:
            # Handle pagination - check if there's a next page button
            next_page_btn = response.xpath('//a[contains(@class, "pagination-next") or contains(@class, "next") or contains(text(), "Next")]')
            
            if next_page_btn:
                # Construct next page URL with the updated structure
                next_page = current_page + 1
                params = {'location': current_location, 'page': next_page}
                if category_id is not None:
                    params['industries'] = str(category_id)
                
                next_url = f"https://www.peopleperhour.com/hire-freelancers?{urlencode(params)}"
                
                self.logger.info(f"Moving to next page: {next_url}")
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={
                        "category_key": current_category_key,
                        "category_data": category_data,
                        "location": current_location,
                        "location_data": location_data,
                        "page": next_page
                    }
                )
            else:
                # No more pages for this category/location combination
                # Move to the next location or category
                self.logger.info(f"No next page button for {current_category_key}/{current_location}, moving to next")
                yield from self._move_to_next_location_or_category(response)
        else:
            # No results on this page, move to next location or category
            self.logger.info(f"No freelancer cards for {current_category_key}/{current_location}, moving to next")
            yield from self._move_to_next_location_or_category(response)

    def _move_to_next_location_or_category(self, response):
        """Helper method to move to the next location or category"""
        current_category_key = response.meta.get("category_key")
        category_data = response.meta.get("category_data", {})
        category_id = category_data.get('category_id')
        current_location = response.meta.get("location")
        location_data = response.meta.get("location_data", {})
        
        # Find indices of current category and location
        try:
            category_index = self.categories.index(current_category_key)
            location_index = self.location_codes.index(current_location)
            
            # Try moving to the next location first
            if location_index < len(self.location_codes) - 1:
                # Move to next location with the same category
                next_location = self.location_codes[location_index + 1]
                next_location_data = self.location_info.get(next_location, {})
                
                self.logger.info(f"Moving to next location: {next_location} ({next_location_data.get('country_name', '')}) for category {category_data.get('subcategory', '')}")
                
                # Mise à jour de l'URL vers la structure correcte
                params = {'location': next_location}
                if category_id is not None:
                    params['industries'] = str(category_id)
                    
                next_url = f"https://www.peopleperhour.com/hire-freelancers?{urlencode(params)}"
                
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={
                        "category_key": current_category_key,
                        "category_data": category_data,
                        "location": next_location,
                        "location_data": next_location_data,
                        "page": 1
                    }
                )
            # If we've gone through all locations, move to the next category
            elif category_index < len(self.categories) - 1:
                next_category_key = self.categories[category_index + 1]
                next_category_data = self.category_info.get(next_category_key, {})
                next_category_id = next_category_data.get('category_id')
                
                # Reset location to the first one
                first_location = self.location_codes[0]
                first_location_data = self.location_info.get(first_location, {})
                
                self.logger.info(f"Moving to next category: {next_category_data.get('subcategory', '')} ({next_category_data.get('main_category', '')}, ID: {next_category_id}) with location {first_location}")
                
                # Mise à jour de l'URL vers la structure correcte
                params = {'location': first_location}
                if next_category_id is not None:
                    params['industries'] = str(next_category_id)
                    
                next_url = f"https://www.peopleperhour.com/hire-freelancers?{urlencode(params)}"
                
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={
                        "category_key": next_category_key,
                        "category_data": next_category_data,
                        "location": first_location,
                        "location_data": first_location_data,
                        "page": 1
                    }
                )
            else:
                self.logger.info("All categories and locations have been processed.")
        except ValueError as e:
            self.logger.error(f"Error finding category or location index: {e}")
            
            # Try to recover by starting with the first category and location
            if self.categories and self.location_codes:
                first_category_key = self.categories[0]
                first_location = self.location_codes[0]
                first_category_data = self.category_info.get(first_category_key, {})
                first_category_id = first_category_data.get('category_id')
                
                self.logger.info(f"Recovering by starting with first category and location: {first_category_key}, {first_location}")
                
                params = {'location': first_location}
                if first_category_id is not None:
                    params['industries'] = str(first_category_id)
                    
                next_url = f"https://www.peopleperhour.com/hire-freelancers?{urlencode(params)}"
                
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={
                        "category_key": first_category_key,
                        "category_data": first_category_data,
                        "location": first_location,
                        "location_data": self.location_info.get(first_location, {}),
                        "page": 1
                    }
                )

    def parse_detail(self, response):
        card_data = response.meta["card_data"]
        freelancer_id = card_data.get("freelancer_url")
        
        # Récupérer les données de catégorie
        category_key = card_data.get("category", "")
        category_data = card_data.get("category_data", {})

        # Extract freelancer name
        name = response.xpath('//div[@class="member-name clearfix"]//h1/text()').get('').strip()
        
        # Extract job title
        job_title = response.xpath('//p[@class="member-job"]/text()').get('').strip()
        
        # Extract location (country)
        location = response.xpath('//div[@class="member-location"]/p/text()').get('').strip()
        country_name = None
        country_id = None
        
        if location:
            # Extract country from "City, Country" format
            parts = location.split(',')
            if len(parts) > 1:
                country_name = parts[-1].strip()
                # Try to find matching country in our countries data
                country_match = next((country for country in self.countries 
                                     if country['name'] == country_name), None)
                if country_match:
                    country_id = country_match['_id']
        
        # Use provided location data if no country found
        if not country_id:
            country_id = card_data.get('location_data', {}).get('country_id')
            country_name = card_data.get('location_data', {}).get('country_name')
            
        # Fallback to displayed country on card
        if not country_name:
            country_name = card_data.get('displayed_country')
        
        # Extract hourly rate
        price = response.xpath('//span[@class="member-cost"]/div[1]/text()').get()
        if price:
            price = price.replace('€', '').replace('£', '').replace('$', '').replace(',', '').strip()
        
        # Extract rating
        rating = response.xpath('//div[@class="total-rating"]/text()').get()
        
        # Extract reviews count
        reviews_count = response.xpath('//div[@class="total-reviews"]/text()').re_first(r'\((\d+)\)')
        
        # Extract avatar/photo
        avatar = response.xpath('//div[contains(@class, "user-avatar")]//img/@src').get()
        
        # Extract description/about
        about_text_parts = response.xpath('//div[contains(@class, "about-container")]//text()').getall()
        description = ' '.join([text.strip() for text in about_text_parts if text.strip()])

        # Try to get full description if available
        full_description = response.xpath('//span[contains(@class, "js-about-full-text")]/text()').get()
        if full_description and full_description.strip():
            description = full_description.strip()
        
        # Extract skills
        skills = response.xpath('//div[contains(@class, "skill-tags")]//a[contains(@class, "tag-item")]/text()').getall()
        skills = [skill.strip() for skill in skills if skill.strip()]
        
        # Extract projects count
        projects_count = response.xpath('//div[contains(@class, "insights-label") and contains(text(), "Projects worked on")]/following-sibling::div[contains(@class, "insights-value")]/text()').get()
        if projects_count:
            projects_count = projects_count.strip()
        
        # Extract industry expertise
        industry_expertise = response.xpath('//div[contains(@class, "industry-expertise-list")]/text()').get()
        if industry_expertise:
            industry_expertise = industry_expertise.replace('Industry expertise:', '').strip()
        
        # Standardize Freelancer according to the model
        freelancer_item = {
            '_type': 'freelancer',
            'url': freelancer_id,
            'url_of_search': response.url,
            'name': name or card_data.get('freelancer_name'),
            'thumbnail': avatar or card_data.get('freelancer_avatar'),
            'title': job_title or card_data.get('title'),
            'description': description,
            'skills': skills or card_data.get('tags', []),
            'rating': float(rating) if rating else float(card_data.get('freelancer_rating', 0)) if card_data.get('freelancer_rating') else None,
            'reviews_count': int(reviews_count) if reviews_count else int(card_data.get('freelancer_reviews', 0)) if card_data.get('freelancer_reviews') else None,
            'hourly_rate': float(price) if price else None,
            'min_price': float(price) if price else None,
            'max_price': None,
            'country_id': country_id,
            'country_name': country_name,
            'source': 'PeoplePerHour',
            'source_id': card_data.get('source_id'),
            'pictures': [],
            'created_at': datetime.utcnow().isoformat(),
            'is_verified': True,
            'industry_expertise': industry_expertise,
            'projects_count': projects_count,
            'category': category_key,
            'main_category': category_data.get('main_category'),
            'subcategory': category_data.get('subcategory'),
            'category_id': category_data.get('category_id')
        }
        
        # Extract reviews from the page
        review_blocks = response.xpath('//li[contains(@class, "item participant feedback")] | //div[contains(@class, "review-card")]')
        for review in review_blocks:
            reviewer_name = review.xpath('.//h6[contains(@class, "participant-name")]/text() | .//span[contains(@class, "review-author")]/text()').get(default='').strip()
            
            # Get rating from active star elements
            rating_spans = review.xpath('.//div[contains(@class, "feedback-rating")]//span[contains(@class, "active")]').getall()
            rating = len(rating_spans) if rating_spans else None
            
            # Extract review text
            text = " ".join([
                t.strip() for t in review.xpath('.//div[contains(@class, "right-col")]/p/text()').getall() if t.strip()
            ])
            
            # Extract date
            date = review.xpath('.//time[@class="message-time"]/@title | .//div[@class="left-col"]/time/@title').get()
            if date:
                # Convert date if needed
                try:
                    # Example format: "Wed, 23 Apr 2025 at 1:15pm"
                    date = date.split('at')[0].strip()
                except:
                    pass
            
            # Extract profile picture
            picture = review.xpath('.//div[@class="left-col"]//img[contains(@class, "user-avatar")]/@src').get()
            
            # Extract location
            location = review.xpath('.//div[contains(@class, "participant-location")]/text()').get(default='').strip()
            
            review_item = {
                '_type': 'review',
                'freelancer_id': freelancer_id,
                'author': reviewer_name,
                'rating': rating,
                'picture': picture,
                'text': text,
                'title': None,
                'created_at': date,
                'location': location,
                'source': 'PeoplePerHour',
                'source_id': card_data.get('source_id'),
                'category': category_key,
                'main_category': category_data.get('main_category'),
                'subcategory': category_data.get('subcategory'),
                'category_id': category_data.get('category_id')
            }
            
            # Write to the file
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(review_item, ensure_ascii=False) + "\n")
            
            yield review_item

        # Extract portfolio items
        portfolio_items = response.xpath('//div[@id="portfolio"]//div[contains(@class, "portfolio-item-container")]')
        for item in portfolio_items:
            title = item.xpath('.//a[contains(@class, "portfolio-grid-item")]/@title').get()
            image = item.xpath('.//div[contains(@class, "portfolio-image-preview")]/@style').re_first(r'url\([\'"](.+?)[\'"]\)')
            
            if title or image:
                portfolio_item = {
                    'title': title,
                    'image': image,
                    'freelancer_id': freelancer_id
                }
                freelancer_item['pictures'].append(portfolio_item)
        
        # Extract service offers/hourlies
        hourlies = response.xpath('//div[@id="offers"]//div[contains(@class, "hourlie-item")]')
        for hourlie in hourlies:
            hourlie_title = hourlie.xpath('.//h6[contains(@class, "hourlie__title")]/a/text()').get('').strip()
            hourlie_price = hourlie.xpath('.//div[contains(@class, "hourlie__price")]//span/text()').get()
            hourlie_url = hourlie.xpath('.//h6[contains(@class, "hourlie__title")]/a/@href').get()
            
            if hourlie_title and hourlie_url:
                service_item = {
                    '_type': 'service',
                    'freelancer_id': freelancer_id,
                    'title': hourlie_title,
                    'price': hourlie_price,
                    'url': hourlie_url,
                    'description': None,
                    'source': 'PeoplePerHour',
                    'source_id': card_data.get('source_id'),
                    'category': category_key,
                    'main_category': category_data.get('main_category'),
                    'subcategory': category_data.get('subcategory'),
                    'category_id': category_data.get('category_id')
                }

                # Write to the file
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(service_item, ensure_ascii=False) + "\n")
                
                yield service_item

        # Write freelancer data to file
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(freelancer_item, ensure_ascii=False) + "\n")
        
        yield freelancer_item 