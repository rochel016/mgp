from odoo import models, fields

class Fokontany(models.Model):
    _name = 'mgp.loc_fokontany'
    _description = "MGP Paramétrage des fokontany"

    name = fields.Char(string="Nom", required=True)
    commune_id = fields.Many2one('mgp.loc_commune',
        ondelete='cascade', string="Commune", required=True)
    
    _sql_constraints = [
                     ('name_unique', 
                      'unique(commune_id, name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]