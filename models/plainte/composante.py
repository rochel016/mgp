from odoo import models, fields

class Composante(models.Model):
    _name = 'mgp.plainte_composante'
    _description = "MGP Paramétrage des composantes de plaintes"

    name = fields.Char(string="Nom", required=True)
    
    _sql_constraints = [
                     ('name_unique', 
                      'unique(name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]