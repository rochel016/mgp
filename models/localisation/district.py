from odoo import models, fields

class District(models.Model):
    _name = 'mgp.loc_district'
    _description = "MGP Paramétrage des districts"

    name = fields.Char(string="Nom", required=True)
    description = fields.Text()
    region_id = fields.Many2one('mgp.loc_region',
        ondelete='cascade', string="Region", required=True)
    
    _sql_constraints = [
                     ('name_unique', 
                      'unique(name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]