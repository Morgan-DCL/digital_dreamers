#!/bin/bash

# Naviguer au répertoire de votre projet
cd /chemin/vers/votre/projet

# Activer l'environnement Python
source /chemin/vers/env/bin/activate

# Exécuter le script Python
python /chemin/vers/votre/script.py

# Ajouter les changements à Git
git add -A

# Commit les changements avec la date et l'heure actuelle comme message
git commit -m "Mise à jour de la base de données : $(date)"

# Pousser les changements sur GitHub
git push origin main
