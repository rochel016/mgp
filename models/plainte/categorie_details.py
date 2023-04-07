from odoo import models, fields

class CategorieDetails(models.Model):
    _name = 'mgp.plainte_categorie_details'
    _description = "MGP Paramétrage des details des catégories des plaintes"

    name = fields.Char(string="Nom", required=True)
    description = fields.Text()
    categorie_id = fields.Many2one('mgp.plainte_categorie',
        ondelete='cascade', string="Catégorie", required=True)

    _sql_constraints = [
                     ('name_unique', 
                      'unique(categorie_id, name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]