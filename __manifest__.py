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
    'version': '1.0.0 - Beta 4',
    'depends': ['base', 'mail', 'board'],
    'qweb': [
        'static/src/xml/icon_systray.xml'],
    'data': [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",

        # Data
        'data/mail_cron.xml',

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
        "views/plainte/sms_view.xml",

         # Paramétrage des citoyens
        "views/citoyen/education_view.xml",
        "views/citoyen/tranche_view.xml",

        # Paramétrage des localisations
        "views/localisation/province_view.xml",
        "views/localisation/region_view.xml",
        "views/localisation/district_view.xml",
        "views/localisation/commune_view.xml",
        "views/localisation/fokontany_view.xml",

        # template EMAIL
        "static/src/xml/mail_template.xml",

        #Tableau de bord
        "views/dashboard/dashboard_prea.xml",
        "views/dashboard/dashboard_pmo.xml",

        # Gestion des menus
        'static/src/xml/menu.xml',

        # Reports
        "reports/ticket_view.xml",
        "reports/report.xml",
    ],
    
    'application': True,
}
