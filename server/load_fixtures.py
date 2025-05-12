import json
import os
from pymongo import MongoClient
from bson import ObjectId

# Connexion à MongoDB
def get_db_connection():
    try:
        # Paramètres de connexion (à ajuster selon votre configuration)
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
        
        # Informations d'authentification
        username = "admin"
        password = "password"
        
        # Si les informations d'authentification sont fournies, les inclure dans l'URI
        if username and password:
            # Extraire le protocole et le reste de l'URI
            if '://' in mongo_uri:
                protocol, rest = mongo_uri.split('://', 1)
                mongo_uri = f"{protocol}://{username}:{password}@{rest}"
        
        client = MongoClient(mongo_uri)
        db = client['develly_scraper']  # Nom de la base de données
        print("Connexion à MongoDB réussie")
        return db
    except Exception as e:
        print(f"Erreur de connexion à MongoDB: {e}")
        exit(1)

def load_countries():
    db = get_db_connection()
    
    # Vérifier si la collection existe déjà
    if 'countries' in db.list_collection_names() and db.countries.count_documents({}) > 0:
        print("La collection des pays existe déjà et contient des données")
        return
    
    # Charger les pays depuis le fichier JSON
    try:
        # Chemin relatif au répertoire racine du projet
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common', 'countries.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
        
        # Convertir les IDs en ObjectId pour MongoDB
        for country in countries:
            if '_id' in country:
                country["_id"] = ObjectId(country["_id"])
        
        # Insertion dans la base de données
        result = db.countries.insert_many(countries)
        print(f"Insertion réussie: {len(result.inserted_ids)} pays insérés")
    except Exception as e:
        print(f"Erreur lors de l'insertion des pays: {e}")

def load_sources():
    db = get_db_connection()
    
    # Vérifier si la collection existe déjà
    if 'sources' in db.list_collection_names() and db.sources.count_documents({}) > 0:
        print("La collection des sources existe déjà et contient des données")
        return
    
    # Charger les sources depuis le fichier JSON
    try:
        # Chemin relatif au répertoire racine du projet
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common', 'sources.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            sources = json.load(f)
        
        # Convertir les IDs en ObjectId pour MongoDB
        for source in sources:
            if '_id' in source:
                source["_id"] = ObjectId(source["_id"])
        
        # Insertion dans la base de données
        result = db.sources.insert_many(sources)
        print(f"Insertion réussie: {len(result.inserted_ids)} sources insérées")
    except Exception as e:
        print(f"Erreur lors de l'insertion des sources: {e}")

if __name__ == "__main__":
    print("Chargement des fixtures pour sources et countries...")
    
    # Chargement des pays
    load_countries()
    
    # Chargement des sources
    load_sources()
    
    print("Terminé!") 