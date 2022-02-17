from odoo import models, fields, api
from datetime import datetime

class Reponse(models.Model):
    _name = 'mgp.plainte_reponse'
    _description = "Réponses des plaintes"
    _order = "plainte_id asc"

    plainte_id = fields.Many2one('mgp.plainte', ondelete='cascade', string="Plainte", required=True)
    reponse = fields.Text(string="Réponses", required=True)

    # attached file for each answer
    upload_file = fields.Binary(string="Fichier")
    file_name = fields.Char(string="Nom du fichier")

    # Contrainte d'unicité
    _sql_constraints = [
                     ('reponse_unique', 
                      'unique(plainte_id, reponse)',
                      'Cette réponse est déjà enregistrée!')
    ]
