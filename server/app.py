from flask import Flask, jsonify, request
from flask_cors import CORS
from bson.objectid import ObjectId
import os
from datetime import datetime

from models import Country, Freelancer, Project, Service, Review
from db import db, initialize_db, JSONEncoder

app = Flask(__name__)
# Allow CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration de l'application
app.json_encoder = JSONEncoder
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def index():
    return jsonify({"message": "Bienvenue sur l'API de Develly Scraper"})

# Routes pour les Freelancers
@app.route('/api/freelancers', methods=['GET'])
def get_freelancers():
    # Support pour les filtres par pays, skills, etc.
    filters = {}
    
    # Filtrer par pays si spécifié
    country_code = request.args.get('country')
    if country_code:
        country = db.countries.find_one({"code": country_code.upper()})
        if country:
            filters['country_id'] = str(country['_id'])
    
    # Filtrer par compétence si spécifié
    skill = request.args.get('skill')
    if skill:
        # Pour MongoDB, on peut rechercher dans un tableau avec l'opérateur $in
        filters['skills'] = {"$in": [skill]}
    
    # Support pour la pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    skip = (page - 1) * limit
    
    # Récupérer les freelancers avec pagination et filtres
    freelancers = list(db.freelancers.find(filters).skip(skip).limit(limit))
    total = db.freelancers.count_documents(filters)
    
    return jsonify({
        "data": [{**doc, '_id': str(doc['_id'])} for doc in freelancers],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    })

@app.route('/api/freelancers/<freelancer_id>', methods=['GET'])
def get_freelancer(freelancer_id):
    try:
        freelancer = db.freelancers.find_one({"_id": ObjectId(freelancer_id)})
        if not freelancer:
            return jsonify({"error": "Freelancer non trouvé"}), 404
        
        # Convertir l'ObjectId en string pour le JSON
        freelancer['_id'] = str(freelancer['_id'])
        
        return jsonify(freelancer)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Routes pour les Pays
@app.route('/api/countries', methods=['GET'])
def get_countries():
    countries = list(db.countries.find())
    return jsonify([{**doc, '_id': str(doc['_id'])} for doc in countries])

@app.route('/api/countries/<country_id>', methods=['GET'])
def get_country(country_id):
    try:
        country = db.countries.find_one({"_id": ObjectId(country_id)})
        if not country:
            return jsonify({"error": "Pays non trouvé"}), 404
        
        country['_id'] = str(country['_id'])
        return jsonify(country)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Routes pour les Projets
@app.route('/api/projects', methods=['GET'])
def get_projects():
    # Support pour la pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    skip = (page - 1) * limit
    
    projects = list(db.projects.find().skip(skip).limit(limit))
    total = db.projects.count_documents({})
    
    return jsonify({
        "data": [{**doc, '_id': str(doc['_id'])} for doc in projects],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    })

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    try:
        project = db.projects.find_one({"_id": ObjectId(project_id)})
        if not project:
            return jsonify({"error": "Projet non trouvé"}), 404
        
        project['_id'] = str(project['_id'])
        return jsonify(project)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Routes pour les Services
@app.route('/api/services', methods=['GET'])
def get_services():
    filters = {}
    
    # Filtre par durée maximale (en jours)
    max_duration = request.args.get('max_duration')
    if max_duration and max_duration.isdigit():
        filters['duration'] = {"$lte": int(max_duration)}
    
    # Filtre par fourchette de prix
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    if min_price or max_price:
        price_filter = {}
        if min_price and min_price.isdigit():
            price_filter["$gte"] = float(min_price)
        if max_price and max_price.isdigit():
            price_filter["$lte"] = float(max_price)
        
        if price_filter:
            filters['price'] = price_filter
    
    # Filtrer par freelancer si spécifié
    freelancer_id = request.args.get('freelancer_id')
    if freelancer_id:
        try:
            # Vérifier si le freelancer existe
            freelancer = db.freelancers.find_one({"_id": ObjectId(freelancer_id)})
            if not freelancer:
                return jsonify({"error": "Freelancer non trouvé"}), 404
            filters['freelancer_id'] = str(freelancer_id)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    # Pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    skip = (page - 1) * limit
    
    services = list(db.services.find(filters).skip(skip).limit(limit))
    total = db.services.count_documents(filters)
    
    return jsonify({
        "data": [{**doc, '_id': str(doc['_id'])} for doc in services],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    })

@app.route('/api/services/<service_id>', methods=['GET'])
def get_service(service_id):
    try:
        service = db.services.find_one({"_id": ObjectId(service_id)})
        if not service:
            return jsonify({"error": "Service non trouvé"}), 404
        
        service['_id'] = str(service['_id'])
        return jsonify(service)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Routes pour les Reviews
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    # Support pour le filtrage par note minimale
    filters = {}
    min_rating = request.args.get('min_rating')
    if min_rating and min_rating.replace('.', '', 1).isdigit():
        filters['rating'] = {"$gte": float(min_rating)}
    
    # Filtrer par freelancer si spécifié
    freelancer_id = request.args.get('freelancer_id')
    if freelancer_id:
        try:
            # Log pour débogage
            print(f"Filtering reviews by freelancer_id: {freelancer_id}")
            
            # Vérifier si le freelancer existe
            try:
                freelancer_obj_id = ObjectId(freelancer_id)
                freelancer = db.freelancers.find_one({"_id": freelancer_obj_id})
                if not freelancer:
                    print(f"Freelancer not found with ObjectId: {freelancer_id}")
                    # Essayer une recherche directe avec la chaîne
                    freelancer = db.freelancers.find_one({"_id": freelancer_id})
                    if not freelancer:
                        print(f"Freelancer not found with string ID either: {freelancer_id}")
                        return jsonify({"error": "Freelancer non trouvé"}), 404
            except Exception as e:
                print(f"Error converting to ObjectId: {str(e)}, trying string match")
                # Si conversion en ObjectId échoue, essayer avec la chaîne directement
                freelancer = db.freelancers.find_one({"_id": freelancer_id})
                if not freelancer:
                    print(f"Freelancer not found with string ID: {freelancer_id}")
                    return jsonify({"error": "Freelancer non trouvé"}), 404
            
            # À ce stade, nous avons trouvé le freelancer, donc nous pouvons filtrer
            filters['freelancer_id'] = freelancer_id
            print(f"Filter applied: {filters}")
            
        except Exception as e:
            print(f"Exception in freelancer_id filter: {str(e)}")
            return jsonify({"error": str(e)}), 400
    
    # Pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    skip = (page - 1) * limit
    
    # Récupérer la liste des reviews
    print(f"Executing find with filters: {filters}")
    reviews = list(db.reviews.find(filters).skip(skip).limit(limit))
    print(f"Found {len(reviews)} reviews")
    total = db.reviews.count_documents(filters)
    
    # Option pour inclure les données des freelancers
    include_freelancers = request.args.get('include_freelancers', 'false').lower() == 'true'
    
    if include_freelancers:
        # Préparer la réponse avec les données des freelancers
        result = []
        for review in reviews:
            review_data = {**review, '_id': str(review['_id'])}
            try:
                # Récupérer le freelancer associé à cette review
                if 'freelancer_id' in review:
                    freelancer = db.freelancers.find_one({"_id": ObjectId(review['freelancer_id'])})
                    if freelancer:
                        # S'assurer que l'ObjectId est converti en chaîne et que tous les champs requis sont présents
                        freelancer_data = {**freelancer, '_id': str(freelancer['_id'])}
                        # S'assurer que les champs nécessaires sont présents, même s'ils sont null
                        required_fields = [
                            'name', 'country_id', 'main_skill', 'hourly_rate', 
                            'min_price', 'max_price', 'created_at', 'source', 
                            'rating', 'reviews_count', 'skills'
                        ]
                        for field in required_fields:
                            if field not in freelancer_data:
                                freelancer_data[field] = None
                                
                        review_data['freelancer'] = freelancer_data
            except Exception as e:
                print(f"Erreur lors de la récupération du freelancer pour la review {review['_id']}: {str(e)}")
                pass
            result.append(review_data)
        
        return jsonify({
            "data": result,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        })
    else:
        # Format de réponse standard
        return jsonify({
            "data": [{**doc, '_id': str(doc['_id'])} for doc in reviews],
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        })

@app.route('/api/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    try:
        review = db.reviews.find_one({"_id": ObjectId(review_id)})
        if not review:
            return jsonify({"error": "Review non trouvée"}), 404
        
        review['_id'] = str(review['_id'])
        return jsonify(review)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour obtenir des statistiques globales et des données d'analyse
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        # Support pour les filtres
        filters = {}
        
        # Filtrer par pays si spécifié
        country_code = request.args.get('country')
        if country_code:
            country = db.countries.find_one({"code": country_code.upper()})
            if country:
                filters['country_id'] = str(country['_id'])
        
        # Filtrer par compétence si spécifié
        skill = request.args.get('skill')
        if skill:
            filters['$or'] = [
                {"skills": {"$in": [skill]}},
                {"main_skill": skill}
            ]
        
        # Filtrer par source si spécifié
        source = request.args.get('source')
        if source:
            filters['source'] = source
        
        # Filtrer par taux horaire min/max
        min_rate = request.args.get('min_rate')
        max_rate = request.args.get('max_rate')
        
        if min_rate or max_rate:
            hourly_rate_filter = {}
            if min_rate and min_rate.replace('.', '', 1).isdigit():
                hourly_rate_filter["$gte"] = float(min_rate)
            if max_rate and max_rate.replace('.', '', 1).isdigit():
                hourly_rate_filter["$lte"] = float(max_rate)
            
            if hourly_rate_filter:
                filters['hourly_rate'] = hourly_rate_filter
        
        # Filtrer par note minimale
        min_rating = request.args.get('min_rating')
        if min_rating and min_rating.replace('.', '', 1).isdigit():
            filters['rating'] = {"$gte": float(min_rating)}

        # Statistiques de base
        stats = {
            "freelancers_count": db.freelancers.count_documents(filters),
            "countries_count": db.countries.count_documents({}),
            "services_count": db.services.count_documents({}),
            "reviews_count": db.reviews.count_documents({}),
            "avg_rating": 0,
            "top_countries": [],
            "top_skills": [],
            "hourly_rate_distribution": [],
            "rating_distribution": [],
            "source_distribution": [],
            "signup_by_month": []
        }
        
        # Freelancers filtrés pour les analyses
        freelancers = list(db.freelancers.find(filters))
        
        # Calculer la note moyenne
        if freelancers:
            # Utiliser une list comprehension pour exclure les valeurs None et garantir que ce sont des nombres
            ratings = [f.get('rating', 0) for f in freelancers if f.get('rating') is not None]
            if ratings:  # S'assurer qu'il y a au moins une note valide
                stats["avg_rating"] = round(sum(ratings) / len(ratings), 2)
            else:
                stats["avg_rating"] = 0  # Valeur par défaut si aucune note valide
        
        # Top des pays par nombre de freelancers
        country_pipeline = [
            {"$match": filters} if filters else {"$match": {}},
            {"$group": {"_id": "$country_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_countries_result = list(db.freelancers.aggregate(country_pipeline))
        
        # Récupérer les noms des pays
        for country_stat in top_countries_result:
            try:
                country_id = country_stat["_id"]
                if country_id:
                    country = db.countries.find_one({"_id": ObjectId(country_id)})
                    if country:
                        stats["top_countries"].append({
                            "name": country["name"],
                            "code": country["code"],
                            "count": country_stat["count"]
                        })
            except Exception:
                pass
        
        # Distribution des compétences principales
        skill_pipeline = [
            {"$match": filters} if filters else {"$match": {}},
            {"$group": {"_id": "$main_skill", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_skills_result = list(db.freelancers.aggregate(skill_pipeline))
        stats["top_skills"] = [{"name": skill["_id"], "count": skill["count"]} for skill in top_skills_result if skill["_id"]]
        
        # Distribution des taux horaires
        rate_ranges = [
            {"min": 0, "max": 20, "label": "$0-20"},
            {"min": 20, "max": 40, "label": "$20-40"},
            {"min": 40, "max": 60, "label": "$40-60"},
            {"min": 60, "max": 80, "label": "$60-80"},
            {"min": 80, "max": 100, "label": "$80-100"},
            {"min": 100, "max": 150, "label": "$100-150"},
            {"min": 150, "max": float('inf'), "label": "$150+"}
        ]
        
        for rate_range in rate_ranges:
            # Construire la requête MongoDB correctement
            query = {**filters}
            
            if rate_range["max"] == float('inf'):
                query["hourly_rate"] = {"$ne": None, "$gte": rate_range["min"]}
            else:
                query["hourly_rate"] = {"$ne": None, "$gte": rate_range["min"], "$lt": rate_range["max"]}
                
            count = db.freelancers.count_documents(query)
            
            if count > 0:
                stats["hourly_rate_distribution"].append({
                    "range": rate_range["label"],
                    "count": count
                })
        
        # Distribution des notes
        for rating in range(1, 6):
            # Utiliser un $match qui exclut explicitement les valeurs nulles
            query = {**filters}
            query["rating"] = {
                "$ne": None,  # Exclure les ratings null
                "$gte": rating - 0.5, 
                "$lt": rating + 0.5
            }
            
            count = db.freelancers.count_documents(query)
            stats["rating_distribution"].append({
                "rating": rating,
                "count": count
            })
        
        # Distribution des sources
        source_pipeline = [
            {"$match": filters} if filters else {"$match": {}},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        source_result = list(db.freelancers.aggregate(source_pipeline))
        stats["source_distribution"] = [{"source": source["_id"] or "Unknown", "count": source["count"]} for source in source_result]
        
        # Inscriptions par mois
        if freelancers:
            signups_by_month = {}
            for freelancer in freelancers:
                if 'created_at' in freelancer and freelancer['created_at'] is not None:
                    date = freelancer['created_at']
                    if isinstance(date, str):
                        try:
                            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        except (ValueError, TypeError):
                            continue  # Ignorer les dates mal formatées
                    
                    try:
                        month_year = f"{date.year}-{date.month:02d}"
                        if month_year not in signups_by_month:
                            signups_by_month[month_year] = 0
                        signups_by_month[month_year] += 1
                    except (AttributeError, TypeError):
                        continue  # Ignorer si date n'a pas les attributs year/month
            
            # Convertir en liste triée par date
            stats["signup_by_month"] = [
                {"month": month, "count": count}
                for month, count in sorted(signups_by_month.items())
            ]
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Routes pour récupérer les compétences disponibles
@app.route('/api/skills', methods=['GET'])
def get_skills():
    try:
        # Récupérer les compétences distinctes des freelancers
        pipeline = [
            {"$match": {"skills": {"$exists": True, "$ne": []}}}, 
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills"}},
            {"$sort": {"_id": 1}}
        ]
        
        skills_cursor = db.freelancers.aggregate(pipeline)
        skills = [doc["_id"] for doc in skills_cursor if doc["_id"]]
        
        # Ajouter également les compétences principales qui pourraient ne pas être dans les tableaux skills
        pipeline_main = [
            {"$match": {"main_skill": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$main_skill"}},
            {"$sort": {"_id": 1}}
        ]
        
        main_skills_cursor = db.freelancers.aggregate(pipeline_main)
        main_skills = [doc["_id"] for doc in main_skills_cursor if doc["_id"]]
        
        # Combiner les deux ensembles et éliminer les doublons
        all_skills = list(set(skills + main_skills))
        all_skills.sort()
        
        return jsonify(all_skills)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Routes pour récupérer les sources disponibles
@app.route('/api/sources', methods=['GET'])
def get_sources():
    try:
        # Récupérer les sources distinctes des freelancers
        pipeline = [
            {"$match": {"source": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$source"}},
            {"$sort": {"_id": 1}}
        ]
        
        sources_cursor = db.freelancers.aggregate(pipeline)
        sources = [doc["_id"] for doc in sources_cursor if doc["_id"]]
        
        return jsonify(sources)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route de débogage pour examiner la structure des documents
@app.route('/api/debug/reviews/<freelancer_id>', methods=['GET'])
def debug_reviews(freelancer_id):
    try:
        # Chercher des reviews avec ce freelancer_id
        reviews_with_id = list(db.reviews.find({'freelancer_id': freelancer_id}).limit(5))
        
        # Obtenir aussi quelques documents de référence
        sample_reviews = list(db.reviews.find().limit(5))
        
        # Obtenir les informations sur le freelancer
        freelancer = None
        try:
            freelancer = db.freelancers.find_one({"_id": ObjectId(freelancer_id)})
        except:
            try:
                freelancer = db.freelancers.find_one({"_id": freelancer_id})
            except:
                pass
        
        # Convertir les ObjectId en strings pour la sérialisation JSON
        if freelancer:
            freelancer['_id'] = str(freelancer['_id'])
        
        for review in reviews_with_id + sample_reviews:
            if '_id' in review:
                review['_id'] = str(review['_id'])
        
        return jsonify({
            'freelancer': freelancer,
            'reviews_count_with_id': len(reviews_with_id),
            'reviews_with_id': reviews_with_id,
            'sample_reviews': sample_reviews,
            'sample_reviews_ids': [r.get('freelancer_id') for r in sample_reviews if 'freelancer_id' in r]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialiser la base de données
    initialize_db()
    
    # Lancer le serveur
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 