#!/usr/bin/env python
"""
Script de démarrage pour le serveur API Flask.
"""

import os
from app import app
from db import initialize_db

if __name__ == "__main__":
    # Initialiser la base de données
    initialize_db()
    
    # Configurer le port (utiliser variable d'environnement ou par défaut 5000)
    port = int(os.environ.get('PORT', 5000))
    
    # Démarrer le serveur
    print(f"Démarrage du serveur sur le port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True) 