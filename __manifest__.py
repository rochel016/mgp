# -*- coding: utf-8 -*-
{
    'name': "MGP",
    'summary': 'Mecanisme de gestion des plaintes',
    'description': """
        Le système Mécanisme de Gestion des Plaintes (MGP) permet de gérer les plaintes et doléances des émetteurs (citoyens),
        de façon accessible et pérenne.
    """,
    'author': "EGM",
    'license': "AGPL-3", 
    'website': "https://digital.gov.mg/",
    # 'category': 'Gouvernance',
    'version': '0.1',
    'depends': ['base', 'mail'],
    'qweb': [
        'static/src/xml/icon_systray.xml'],
    'data': [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",

        # Assets files (js, css)
        "static/src/xml/assets.xml",

        # Gesiton et Suivi des plaintes
        "views/plainte/select_pmo_view.xml",
        "views/plainte/plainte_bpo_view.xml",
        "views/plainte/plainte_prea_view.xml",
        "views/plainte/plainte_pmo_view.xml",

        # Paramétrage des plaintes
        "views/plainte/categorie_view.xml",
        "views/plainte/categorie_details_view.xml",
        "views/plainte/composante_view.xml",

         # Paramétrage des citoyens
        "views/citoyen/education_view.xml",
        "views/citoyen/tranche_view.xml",

        # Paramétrage des localisations
        "views/localisation/province_view.xml",
        "views/localisation/region_view.xml",
        "views/localisation/district_view.xml",
        "views/localisation/commune_view.xml",
        "views/localisation/fokontany_view.xml",

        # Gestion des menus
        'static/src/xml/menu.xml',
    ],
    
    'application': True,
}
