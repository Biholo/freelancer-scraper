#!/usr/bin/env python
"""
Script utilitaire pour exécuter les spiders Scrapy depuis le package.
Usage: python -m develly_scraper.crawl [spider_name] [options]
Options:
  -a NAME=VALUE      Définir un paramètre spider (peut être répété)
  --json             Exporter en JSON au lieu de MongoDB
  --limit N          Limiter le nombre d'items extraits
"""

import sys
import os
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def parse_spider_args(args):
    """
    Parse les arguments de type -a NAME=VALUE
    """
    spider_args = {}
    for arg in args:
        if arg.startswith('-a'):
            param = arg[2:].strip()
            name, value = param.split('=', 1)
            spider_args[name] = value
    return spider_args

def run_spider(spider_name=None, use_json=False, item_limit=None, spider_args=None):
    """
    Exécute un spider Scrapy.
    Args:
        spider_name: Le nom du spider à exécuter
        use_json: Si True, utilise le format JSON au lieu de MongoDB
        item_limit: Limite le nombre d'items extraits
        spider_args: Arguments supplémentaires à passer au spider
    """
    available_spiders = [
        "truelancer",
        "peopleperhour",
        "freelancer",
    ]

    if not spider_name:
        print("Spiders disponibles:")
        for spider in available_spiders:
            print(f"- {spider}")
        print("\nUsage: python -m develly_scraper.crawl [spider_name] [options]")
        print("Options:")
        print("  -a NAME=VALUE      Définir un paramètre spider (peut être répété)")
        print("  --json             Exporter en JSON au lieu de MongoDB")
        print("  --limit N          Limiter le nombre d'items extraits")
        return

    settings = get_project_settings()
    
    # Configuration MongoDB avec Docker
    settings.set('MONGO_URI', 'mongodb://admin:password@localhost:27017/')
    settings.set('MONGO_DATABASE', 'develly_scraper')
    
    # Préparer les arguments du spider
    kwargs = spider_args or {}
    
    if use_json:
        # Désactiver MongoDB dans le pipeline
        settings.set('ITEM_PIPELINES', {
            'develly_scraper.pipelines.DateAddingPipeline': 100,
            'develly_scraper.pipelines.TextCleaningPipeline': 200,
        })
        print("Mode JSON activé: les données seront exportées en JSON")
    
    if item_limit:
        settings.set('CLOSESPIDER_ITEMCOUNT', item_limit)
        print(f"Limite d'items fixée à {item_limit}")

    process = CrawlerProcess(settings)
    
    try:
        if spider_name not in available_spiders:
            print(f"⚠️ Attention: Le spider '{spider_name}' n'est pas dans la liste des spiders connus!")
            print("Tentative d'exécution quand même...")
            
        process.crawl(spider_name, **kwargs)
        print(f"🕷️ Démarrage du spider '{spider_name}'...")
        print("⏱️ Ce processus peut prendre plusieurs minutes.")
        if not use_json:
            print("📊 Les données seront stockées dans MongoDB.")
        else:
            print("📊 Les données seront exportées en format JSON.")
        process.start() # Ce processus est bloquant jusqu'à la fin du crawling
        print(f"✅ Spider '{spider_name}' terminé avec succès!")
    except KeyError:
        print(f"❌ Erreur: Le spider '{spider_name}' n'existe pas!")
        print("\nSpiders disponibles:")
        for spider in available_spiders:
            print(f"- {spider}")

def run_all_spiders(use_json=True, item_limit=5, country_code="US"):
    """
    Exécute tous les spiders disponibles avec des paramètres de test.
    """
    available_spiders = [
        "truelancer",
        "peopleperhour",
        "freelancer"
    ]
    
    for spider in available_spiders:
        print(f"\n{'='*50}")
        print(f"Exécution du spider: {spider}")
        print(f"{'='*50}\n")
        spider_args = {"country": country_code}
        run_spider(spider, use_json, item_limit, spider_args)

if __name__ == "__main__":
    # Parser les arguments
    parser = argparse.ArgumentParser(description='Execute Scrapy spiders')
    parser.add_argument('spider', nargs='?', help='Spider name to run')
    parser.add_argument('--json', action='store_true', help='Export to JSON instead of MongoDB')
    parser.add_argument('--limit', type=int, help='Limit the number of items scraped')
    parser.add_argument('--all', action='store_true', help='Run all available spiders')
    parser.add_argument('-a', action='append', dest='spider_args', default=[], 
                        help='Set spider argument (NAME=VALUE)')
    
    # Parser les arguments connus et conserver le reste
    args, unknown = parser.parse_known_args()
    
    # Si -a est utilisé dans unknown, l'extraire
    spider_args = {}
    for arg in args.spider_args:
        name, value = arg.split('=', 1)
        spider_args[name] = value
    
    # Ajouter les arguments inconnus (qui peuvent inclure -a)
    for i in range(len(unknown)):
        if unknown[i].startswith('-a') and i+1 < len(unknown) and '=' in unknown[i+1]:
            name, value = unknown[i+1].split('=', 1)
            spider_args[name] = value
    
    if args.all:
        run_all_spiders(args.json, args.limit, spider_args.get('country', 'US'))
    else:
        run_spider(args.spider, args.json, args.limit, spider_args) 