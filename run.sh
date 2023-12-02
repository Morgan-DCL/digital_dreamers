#!/bin/bash

# Naviguer au répertoire de votre projet
cd ~/scalper/digital_dreamers

# Activer l'environnement Python
source .venv/bin/activate

# Exécuter le script Python
python start.py

# Ajouter les changements à Git
git add -A

# Commit les changements avec la date et l'heure actuelle comme message
git commit -m "update_movies : $(date)"

# Pousser les changements sur GitHub
git push origin main
