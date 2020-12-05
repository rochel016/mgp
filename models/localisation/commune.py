from odoo import models, fields

class Commune(models.Model):
    _name = 'mgp.loc_commune'
    _description = "MGP Paramétrage des communes"

    name = fields.Char(string="Nom", required=True)
    description = fields.Text()
    district_id = fields.Many2one('mgp.loc_district',
        ondelete='cascade', string="District", required=True)
    
    _sql_constraints = [
                     ('name_unique', 
                      'unique(district_id, name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]