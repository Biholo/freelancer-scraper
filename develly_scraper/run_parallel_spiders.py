#!/usr/bin/env python
"""
Script pour lancer les trois spiders en parallèle.
Usage: python run_parallel_spiders.py [--country COUNTRY_CODE] [--category CATEGORY]
"""

import argparse
import logging
import os
import sys
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

# Ajouter le répertoire parent au chemin de recherche des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les spiders
from develly_scraper.spiders.freelancer_spider import FreelancerSpider
from develly_scraper.spiders.truelancer_spider import TrueLancerSpider
from develly_scraper.spiders.peopleperhouer_spider import PeoplePerHourSpider

# Configurer le logger
configure_logging()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scrapy_parallel.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_spiders(country=None, category=None):
    """
    Fonction pour exécuter tous les spiders en parallèle en utilisant twisted.internet.reactor.
    """
    # Obtenir les paramètres de configuration de Scrapy
    settings = get_project_settings()
    
    # Créer un runner de crawler avec les settings
    runner = CrawlerRunner(settings)
    
    # Configurer les paramètres communs pour tous les spiders
    kwargs = {}
    if country:
        kwargs['country'] = country
    if category:
        kwargs['category'] = category
    
    # Liste pour stocker les deferred des spiders
    deferreds = []
    
    # Ajouter chaque spider au runner
    for spider_class in [FreelancerSpider, TrueLancerSpider, PeoplePerHourSpider]:
        logger.info(f"Démarrage du spider {spider_class.name} avec paramètres : pays={country}, catégorie={category}")
        deferred = runner.crawl(spider_class, **kwargs)
        deferreds.append(deferred)
    
    # Après l'exécution de tous les spiders, arrêter le reactor
    from twisted.internet.defer import DeferredList
    dl = DeferredList(deferreds)
    dl.addBoth(lambda _: reactor.stop())
    
    # Démarrer le reactor
    reactor.run()

def main():
    """Fonction principale pour lancer les spiders en parallèle."""
    # Analyser les arguments de la ligne de commande
    parser = argparse.ArgumentParser(description="Lancer les spiders en parallèle")
    parser.add_argument('--country', type=str, help='Code du pays (ex: FR, US, GB)')
    parser.add_argument('--category', type=str, help='Catégorie à scraper')
    args = parser.parse_args()
    
    # Avertissement si aucun filtre n'est spécifié
    if not args.country and not args.category:
        logger.warning("Aucun pays ou catégorie spécifié. Les spiders vont utiliser leurs valeurs par défaut et scraper TOUTES les données disponibles.")
        
    if args.country:
        logger.info(f"Filtrage par pays: {args.country}")
    if args.category:
        logger.info(f"Filtrage par catégorie: {args.category}")
    
    logger.info("Démarrage des spiders en parallèle...")
    
    # Exécuter tous les spiders en parallèle
    run_spiders(country=args.country, category=args.category)
    
    logger.info("Tous les spiders ont terminé leur exécution.")

if __name__ == "__main__":
    main() 