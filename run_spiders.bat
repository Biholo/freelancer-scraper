@echo off
echo Demarrage des spiders en parallele...

start cmd /k "scrapy crawl freelancer"
start cmd /k "scrapy crawl truelancer"
start cmd /k "scrapy crawl peopleperhour"

echo Les spiders ont ete lances dans des fenetres separees. 