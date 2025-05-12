from datetime import datetime
import json
from bson import ObjectId
from bson.json_util import dumps, loads

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

class Model:
    def to_json(self):
        """Convertit le document en JSON avec gestion des ObjectId."""
        return JSONEncoder().encode(self.__dict__)
    
    @staticmethod
    def from_json(json_data):
        """Crée une instance à partir de données JSON."""
        return loads(json_data)

class Source(Model):
    collection_name = 'sources'
    
    def __init__(self, name, url=None, description=None, _id=None):
        self._id = _id or ObjectId()
        self.name = name
        self.url = url
        self.description = description
    
    def to_dict(self):
        return {
            '_id': str(self._id),
            'name': self.name,
            'url': self.url,
            'description': self.description
        }

class Country(Model):
    collection_name = 'countries'
    
    def __init__(self, code, name, _id=None):
        self._id = _id or ObjectId()
        self.code = code
        self.name = name
    
    def to_dict(self):
        return {
            '_id': str(self._id),
            'code': self.code,
            'name': self.name
        }

class Freelancer(Model):
    collection_name = 'freelancers'
    
    def __init__(self, url, name=None, title=None, description=None, skills=None, 
                 rating=None, reviews_count=None, hourly_rate=None, min_price=None, 
                 max_price=None, country_id=None, url_of_search=None, main_skill=None, 
                 thumbnail=None, source=None, source_id=None, pictures=None, created_at=None, 
                 is_verified=False, _id=None):
        self._id = _id or ObjectId()
        self.url_of_search = url_of_search
        self.main_skill = main_skill
        self.thumbnail = thumbnail
        self.url = url
        self.source = source
        self.source_id = source_id
        self.pictures = pictures or []
        self.name = name
        self.title = title
        self.description = description
        self.skills = skills or []
        self.rating = rating
        self.reviews_count = reviews_count
        self.hourly_rate = hourly_rate
        self.min_price = min_price
        self.max_price = max_price
        self.country_id = country_id
        self.created_at = created_at or datetime.utcnow()
        self.is_verified = is_verified
    
    def to_dict(self):
        return {
            '_id': str(self._id),
            'url_of_search': self.url_of_search,
            'main_skill': self.main_skill,
            'thumbnail': self.thumbnail,
            'url': self.url,
            'source': self.source,
            'source_id': self.source_id,
            'pictures': self.pictures,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'skills': self.skills,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'hourly_rate': self.hourly_rate,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'country_id': self.country_id,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'is_verified': self.is_verified
        }

class Project(Model):
    collection_name = 'projects'
    
    def __init__(self, title, description=None, delivery_time=None, main_picture=None, 
                 pictures=None, pricing=None, _id=None):
        self._id = _id or ObjectId()
        self.delivery_time = delivery_time
        self.title = title
        self.description = description
        self.main_picture = main_picture
        self.pictures = pictures or []
        self.pricing = pricing
    
    def to_dict(self):
        return {
            '_id': str(self._id),
            'delivery_time': self.delivery_time,
            'title': self.title,
            'description': self.description,
            'main_picture': self.main_picture,
            'pictures': self.pictures,
            'pricing': self.pricing
        }

class Service(Model):
    collection_name = 'services'
    
    def __init__(self, freelancer_id, title, description=None, price=None, duration=None, _id=None):
        self._id = _id or ObjectId()
        self.freelancer_id = freelancer_id
        self.title = title
        self.description = description
        self.price = price
        self.duration = duration
    
    def to_dict(self):
        return {
            '_id': str(self._id),
            'freelancer_id': self.freelancer_id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'duration': self.duration
        }

class Review(Model):
    collection_name = 'reviews'
    
    def __init__(self, freelancer_id, author=None, rating=None, picture=None, 
                 text=None, title=None, created_at=None, _id=None):
        self._id = _id or ObjectId()
        self.freelancer_id = freelancer_id
        self.author = author
        self.rating = rating
        self.picture = picture
        self.text = text
        self.title = title
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            '_id': str(self._id),
            'freelancer_id': self.freelancer_id,
            'author': self.author,
            'rating': self.rating,
            'picture': self.picture,
            'text': self.text,
            'title': self.title,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        } 