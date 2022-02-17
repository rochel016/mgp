from odoo import models, fields

class Region(models.Model):
    _name = 'mgp.loc_region'
    _description = "MGP Paramétrage des régions"

    name = fields.Char(string="Nom", required=True)
    description = fields.Text()
    province_id = fields.Many2one('mgp.loc_province',
        ondelete='cascade', string="Province", required=True)
    
    _sql_constraints = [
                     ('name_unique', 
                      'unique(name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]