# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DevellyScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WebsiteItem(scrapy.Item):
    # Champs pour stocker les informations d'un site web
    title = scrapy.Field()
    paragraphs = scrapy.Field()
    url = scrapy.Field()
    date_scraped = scrapy.Field()


class FreelancerItem(scrapy.Item):
    """Item pour les freelancers de différentes sources"""
    url_of_search = scrapy.Field()
    main_skill = scrapy.Field()
    thumbnail = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    pictures = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    hourly_rate = scrapy.Field()
    min_price = scrapy.Field()
    max_price = scrapy.Field()
    country_id = scrapy.Field()
    created_at = scrapy.Field()
    is_verified = scrapy.Field()


class ReviewItem(scrapy.Item):
    """Item pour les avis/reviews des freelancers"""
    freelancer_id = scrapy.Field()
    author = scrapy.Field()
    rating = scrapy.Field()
    picture = scrapy.Field()
    text = scrapy.Field()
    title = scrapy.Field()
    created_at = scrapy.Field()


class ServiceItem(scrapy.Item):
    """Item pour les services proposés par un freelancer"""
    freelancer_id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field() 
    duration = scrapy.Field()
