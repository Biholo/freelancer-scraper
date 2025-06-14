# Develly Scraper

Un projet de scraping web utilisant Scrapy pour collecter des données de freelances depuis différentes plateformes.

## Architecture du projet

Le projet est divisé en trois parties principales:
- **Scrapers**: Des spiders Scrapy pour collecter les données
- **Backend**: Une API REST en Flask pour accéder aux données collectées
- **Frontend**: Interface utilisateur pour visualiser et analyser les données

## Prérequis

- Python 3.8+
- Docker et Docker Compose
- Git
- Node.js et NPM (pour le développement frontend)

## Installation

1. Clonez le dépôt:
```bash
git clone https://github.com/votre-utilisateur/develly-scraper.git
cd develly-scraper
```

2. Installez les dépendances Python:
```bash
pip install -r requirements.txt
```

## Démarrage de la Base de Données

La base de données MongoDB et son interface d'administration (Mongo Express) peuvent être facilement lancées avec Docker Compose:

```bash
docker-compose up -d mongodb mongo-express
```

Cette commande va:
- Démarrer MongoDB sur le port 27017
- Démarrer MongoDB Express (interface web) sur le port 8081
- Configurer le volume pour la persistance des données

Vous pouvez vérifier que les services sont bien lancés avec:
```bash
docker-compose ps
```

### Accès à MongoDB Express

Une fois lancé, vous pouvez accéder à l'interface web MongoDB Express à l'adresse:
```
http://localhost:8081
```

Identifiants par défaut:
- Utilisateur: admin
- Mot de passe: password

## Démarrage du Backend

### Option 1: Avec Docker Compose

```bash
docker-compose up -d backend
```

### Option 2: Lancement manuel

```bash
cd server
python run.py
```

Le backend sera accessible à l'adresse: http://localhost:5000

Endpoints API disponibles:
- `GET /api/freelancers` - Liste tous les freelancers
- `GET /api/freelancers/<id>` - Détails d'un freelancer
- `GET /api/reviews` - Liste toutes les reviews
- `GET /api/countries` - Liste tous les pays

## Démarrage du Frontend

### Option 1: Avec Docker Compose

```bash
docker-compose up -d frontend
```

### Option 2: Lancement manuel

```bash
cd frontend
npm install # ou yarn install
npm run dev # ou yarn dev
```

Le frontend sera accessible à l'adresse: http://localhost:5173

## Exécution des Scrapers

Les scrapers permettent de collecter des données de freelances depuis différentes plateformes.

### Option 1: Lancement de tous les spiders en parallèle

```bash
run_spiders.bat
```

Cette commande va lancer tous les spiders dans des fenêtres séparées.

### Option 2: Lancement d'un spider spécifique

```bash
scrapy crawl freelancer
```

Remplacez `freelancer` par le nom du spider que vous souhaitez exécuter.

### Option 3: Lancement avec des paramètres spécifiques

```bash
scrapy crawl freelancer -a country=FR -a category=webdesign
```

Paramètres disponibles:
- `country`: Code ISO du pays (ex: FR, US, GB)
- `category`: Catégorie de compétence (ex: webdesign, programming)

### Liste des spiders disponibles

- `freelancer`: Spider pour Freelancer.com
- `truelancer`: Spider pour Truelancer.com
- `peopleperhour`: Spider pour PeoplePerHour.com

Les données collectées seront automatiquement stockées dans MongoDB.

## Démarrage complet de l'application

Pour démarrer tous les services en une seule commande:

```bash
docker-compose up -d
```

## Arrêt des services

Pour arrêter tous les services:

```bash
docker-compose down
```

Pour arrêter un service spécifique:

```bash
docker-compose stop mongodb
```

## Structure des données

### Freelancers
```json
{
  "url_of_search": "https://www.freelancer.com/...",
  "main_skill": "website-design",
  "thumbnail": "https://...",
  "url": "https://...",
  "source": "Freelancer",
  "pictures": ["https://...", "..."],
  "name": "John Doe",
  "title": "Web Designer",
  "description": "...",
  "skills": ["HTML", "CSS", "JavaScript"],
  "rating": 4.9,
  "reviews_count": 120,
  "hourly_rate": 45.0,
  "min_price": 50,
  "max_price": 500,
  "country_id": "...",
  "country_name": "France",
  "created_at": "2023-06-01T12:34:56.789Z",
  "is_verified": true
}
```

## Structure du projet

- `develly_scraper/` - Le package Python du projet Scrapy
  - `spiders/` - Dossier contenant les spiders Scrapy
  - `items.py` - Définition des items pour stocker les données scrapées
  - `pipelines.py` - Pipelines pour traiter les items
  - `middlewares.py` - Middlewares pour gérer les requêtes et réponses
  - `settings.py` - Configuration du projet
- `server/` - Backend API Flask pour accéder aux données
- `frontend/` - Interface utilisateur en Vue.js/React
- `common/` - Fichiers de configuration partagés
- `docker-compose.yml` - Configuration Docker pour tous les services
- `requirements.txt` - Dépendances Python
- `run_spiders.bat` - Script pour lancer tous les spiders en parallèle

## Note sur l'utilisation des données

Ce projet est uniquement à des fins éducatives. Assurez-vous de respecter les conditions d'utilisation des sites que vous scraper.
