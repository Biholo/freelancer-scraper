# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
from pymongo import MongoClient
import os
from bson.objectid import ObjectId


class DevellyScraperPipeline:
    def process_item(self, item, spider):
        return item


class DateAddingPipeline:
    """Pipeline pour ajouter des dates (created_at, updated_at) aux items."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Ajouter la date de création si elle n'existe pas
        if 'created_at' not in adapter:
            adapter['created_at'] = datetime.utcnow()
        # Toujours mettre à jour la date de mise à jour
        adapter['updated_at'] = datetime.utcnow()
        return item


class TextCleaningPipeline:
    """Pipeline pour nettoyer le texte des items."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        text_fields = ['name', 'title', 'description']
        for field in text_fields:
            if field in adapter and adapter[field]:
                # Nettoyer les espaces inutiles
                if isinstance(adapter[field], str):
                    adapter[field] = adapter[field].strip()
        return item


class MongoDBPipeline:
    """Pipeline pour enregistrer les items dans MongoDB."""
    
    collection_name = 'freelancers'
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'develly_scraper')
        )
    
    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # Créer l'index unique pour éviter les doublons
        self.db[self.collection_name].create_index("url", unique=True)
    
    def close_spider(self, spider):
        self.client.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Déterminer la collection en fonction du type d'item
        if '_type' in adapter:
            # Si le champ _type est spécifié, l'utiliser directement
            collection = adapter['_type'] + 's'  # Ajouter un 's' pour le pluriel (ex: 'freelancer' -> 'freelancers')
        elif 'reviews_count' in adapter:  # C'est un freelancer
            collection = 'freelancers'
        elif 'freelancer_id' in adapter and 'author' in adapter:  # C'est une review
            collection = 'reviews'
        elif 'freelancer_id' in adapter and 'price' in adapter:  # C'est un service
            collection = 'services'
        else:
            collection = 'items'
        
        # Ajouter un log pour déboguer la collection utilisée
        spider.logger.debug(f"Collection déterminée pour l'item: {collection}")
        
        # Conversion en dictionnaire pour MongoDB
        item_dict = dict(adapter)
        
        # Si c'est un freelancer, associer la source appropriée
        if collection == 'freelancers' and 'source' in item_dict:
            source_name = item_dict.get('source')
            if source_name:
                # Chercher la source par son nom
                source = self.db['sources'].find_one({"name": source_name})
                if source:
                    # Associer l'ID de la source
                    item_dict['source_id'] = str(source['_id'])
                else:
                    # Créer une nouvelle source si elle n'existe pas
                    new_source_id = ObjectId()
                    self.db['sources'].insert_one({
                        "_id": new_source_id,
                        "name": source_name,
                        "url": item_dict.get('url_of_search', None),
                        "description": f"Source créée automatiquement: {source_name}"
                    })
                    item_dict['source_id'] = str(new_source_id)
        
        # Ajouter les champs de réseaux sociaux s'ils n'existent pas
        if collection == 'freelancers':
            if 'linkedin_link' not in item_dict:
                item_dict['linkedin_link'] = None
            if 'facebook_link' not in item_dict:
                item_dict['facebook_link'] = None
            if 'twitter_link' not in item_dict:
                item_dict['twitter_link'] = None
            
            # S'assurer que _id est un ObjectId (généré automatiquement)
            if '_id' not in item_dict:
                item_dict['_id'] = ObjectId()
        
        # Vérifier si l'item existe déjà
        if 'url' in item_dict:
            existing = self.db[collection].find_one({"url": item_dict["url"]})
            if existing:
                # Mettre à jour
                self.db[collection].update_one({"_id": existing["_id"]}, {"$set": item_dict})
                spider.logger.info(f"Item mis à jour dans MongoDB: {collection} - {item_dict.get('name', 'Anonyme')}")
            else:
                # Insérer
                self.db[collection].insert_one(item_dict)
                spider.logger.info(f"Nouvel item ajouté à MongoDB: {collection} - {item_dict.get('name', 'Anonyme')}")
        else:
            # Pas d'URL, on insère directement
            self.db[collection].insert_one(item_dict)
            spider.logger.info(f"Item ajouté à MongoDB: {collection}")
        
        return item
