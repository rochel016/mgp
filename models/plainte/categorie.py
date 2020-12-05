from odoo import models, fields

class Categorie(models.Model):
    _name = 'mgp.plainte_categorie'
    _description = "MGP Paramétrage des catégories des plaintes"

    name = fields.Char(string="Nom", required=True)
    description = fields.Text()
    
    _sql_constraints = [
                     ('name_unique', 
                      'unique(name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]