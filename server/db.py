"""
Module de gestion de la connexion à la base de données MongoDB.
"""

from pymongo import MongoClient
import os
from bson.objectid import ObjectId
import json
from datetime import datetime

# Configuration de MongoDB
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'develly_scraper')

# Informations d'authentification
username = "admin"
password = "password"

# Si les informations d'authentification sont fournies, les inclure dans l'URI
if username and password:
    # Extraire le protocole et le reste de l'URI
    if '://' in MONGO_URI:
        protocol, rest = MONGO_URI.split('://', 1)
        MONGO_URI = f"{protocol}://{username}:{password}@{rest}"

# Création du client MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Helper pour la sérialisation des ObjectId et datetime en JSON
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def get_collection(collection_name):
    """Récupère une collection MongoDB."""
    return db[collection_name]

def initialize_db():
    """
    Initialise la base de données avec des données de base si nécessaire.
    """
    # Vérifier si la collection des pays existe et contient des données
    if db.countries.count_documents({}) == 0:
        # Ajouter des pays par défaut
        countries = [
            {"code": "FR", "name": "France"},
            {"code": "US", "name": "United States"},
            {"code": "UK", "name": "United Kingdom"},
            {"code": "DE", "name": "Germany"},
            {"code": "ES", "name": "Spain"},
            {"code": "IT", "name": "Italy"},
            {"code": "CA", "name": "Canada"},
            {"code": "AU", "name": "Australia"},
            {"code": "JP", "name": "Japan"},
            {"code": "BR", "name": "Brazil"}
        ]
        db.countries.insert_many(countries)
        print("Données initiales ajoutées à la collection des pays")
    
    # Création d'index pour améliorer les performances
    db.freelancers.create_index("url", unique=True)
    db.freelancers.create_index("country_id")
    
    # Index pour les liens de réseaux sociaux
    db.freelancers.create_index("linkedin_link")
    db.freelancers.create_index("facebook_link")
    db.freelancers.create_index("twitter_link")
    
    db.reviews.create_index("freelancer_id")
    db.services.create_index("freelancer_id")
    
    print("Base de données initialisée avec succès")

def get_freelancer_schema():
    """
    Retourne le schéma de document pour les freelancers.
    Utile pour documenter la structure et pour validation.
    """
    return {
        "_id": "ObjectId - identifiant unique",
        "name": "string - nom du freelancer",
        "url": "string - URL du profil (unique)",
        "thumbnail": "string - URL de l'image miniature",
        "title": "string - titre du profil",
        "description": "string - description du profil",
        "skills": "array - liste des compétences",
        "pictures": "array - liste des URLs des images",
        "rating": "float - note moyenne",
        "reviews_count": "integer - nombre d'avis",
        "country_id": "string - ID du pays",
        "location": "string - localisation",
        "hourly_rate": "float - taux horaire",
        "min_price": "float - prix minimum",
        "max_price": "float - prix maximum",
        "linkedin_link": "string - URL du profil LinkedIn",
        "facebook_link": "string - URL du profil Facebook",
        "twitter_link": "string - URL du profil Twitter",
        "source": "string - source des données (fiverr, upwork, etc.)",
        "created_at": "datetime - date de création",
        "updated_at": "datetime - date de mise à jour"
    }

if __name__ == "__main__":
    # Test de connexion
    initialize_db()
    print(f"Connecté à MongoDB: {MONGO_URI}")
    print(f"Base de données: {DB_NAME}")
    print(f"Collections disponibles: {db.list_collection_names()}")
    print("\nStructure de document pour les freelancers:")
    for key, value in get_freelancer_schema().items():
        print(f"- {key}: {value}") 