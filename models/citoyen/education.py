from odoo import models, fields

class Education(models.Model):
    _name = 'mgp.citoyen_education'
    _description = "MGP Paramétrage des niveaux d'éducation du cytoyen"

    name = fields.Char(string="Nom", required=True) # Ex: Tsy nianatra, primaite, secondaire, bac, universitaire, cadre, ...²
    
    _sql_constraints = [
                     ('name_unique', 
                      'unique(name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]