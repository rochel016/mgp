# -*- coding: utf-8 -*-
{
    'name': "MGP",
    'summary': 'Mecanisme de gestion des plaintes',
    'description': """
        Le système Mécanisme de Gestion des Plaintes (MGP) permet de gérer les plaintes et doléances des émetteurs (citoyens),
        de façon accessible et pérenne.
    """,
    #'category': '',
    'author': "UGD",
    'license': "AGPL-3", 
    'website': "https://digital.gov.mg/",
    'version': '0.6.0 Beta',
    'depends': ['base', 'mail', 'board'],
    'qweb': [
        'static/src/xml/icon_systray.xml',], #'static/src/xml/login.xml'
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
        "views/plainte/plainte_bpo_qualite_view.xml",
        "views/plainte/plainte_bpo_list_search_view.xml", # A appeler dans un popup

        # Paramétrage des plaintes
        "views/plainte/categorie_view.xml",
        "views/plainte/categorie_details_view.xml",
        "views/plainte/composante_view.xml",
        "views/plainte/sms_view.xml",
        "views/plainte/custom_dashboard.xml",

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
        "static/src/xml/email_server.xml",

        #Tableau de bord
        "views/dashboard/dashboard_prea.xml",
        "views/dashboard/dashboard_pmo.xml",

        # Gestion des menus
        'static/src/xml/menu.xml',

        # Reports
        #"reports/ticket_view.xml",
        #"reports/report.xml",

        # Langue
        # "static/src/xml/i18n.xml",
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
