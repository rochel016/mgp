# -*- coding: utf-8 -*-

# Modèles pour la localisation (adresse)
from .localisation import province, region, district, commune, fokontany

# Modèles pour le citoyen
from .citoyen import education, tranche

# Modèles pour la gestion des plaintes
from .plainte import categorie, categorie_details, composante, plainte, log, note, reponse, sms

# Modèles pour les dashboard
from .plainte import custom_dashboard