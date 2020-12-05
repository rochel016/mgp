from odoo import models, fields

class Province(models.Model):
    _name = 'mgp.loc_province'
    _description = "MGP Paramétrage des provinces"

    name = fields.Char(string="Nom", required=True)
    description = fields.Text()

    _sql_constraints = [
                     ('name_unique', 
                      'unique(name)',
                      'Choisissez une autre valeur - elle doit être unique!')
    ]