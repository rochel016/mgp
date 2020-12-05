from odoo import models, fields

class Tranche(models.Model):
    _name = 'mgp.citoyen_tranche'
    _description = "MGP Paramétrage des tranches d'age des citoyens"

    name = fields.Char(string="Nom", required=True) # Ex: Moins de 18 ans, ...
    
    _sql_constraints = [
                     ('name_unique', 
                      'unique(name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]