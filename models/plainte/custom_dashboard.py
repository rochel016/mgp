from odoo import models, fields

class CutomDashboard(models.Model):
    _name = "mgp.custom_dashboard"
 
    name = fields.Char(string="Name", required=True)
    category = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
        ('H', 'H'),
    ], string="Catégorie", required=True)

    # Contrainte d'unicité
    _sql_constraints = [
        ('name_unique',
        'unique(name)', # Nom unique
        'Le nom doit être unique!'),

        ('name_category_unique', 
        'unique(name, category)',
        'Le nom et catégorie existent déjà!')
    ]

    total_citoyens = fields.Integer(string="Total Citoyens", compute="_get_total_citoyens")
    def _get_total_citoyens(self):
        for rec in self:
            if rec.category == 'A':
                count = self.env['mgp.plainte'].search_count([]) 
                rec.total_citoyens = count
            else:
                rec.total_citoyens = 0

    total_femmes = fields.Integer(string="Total Femmes", compute="_get_total_femmes")
    def _get_total_femmes(self):
        for rec in self:
            if rec.category == 'B':
                count = self.env['mgp.plainte'].search_count([('genre','=','feminin')]) 
                rec.total_femmes = count
            else:
                rec.total_femmes = 0
    
    total_hommes = fields.Integer(string="Total Hommes", compute="_get_total_hommes")
    def _get_total_hommes(self):
        for rec in self:
            if rec.category == 'C':
                count = self.env['mgp.plainte'].search_count([('genre','=','masculin')]) 
                rec.total_hommes = count
            else:
                rec.total_hommes = 0
    
    total_mineurs = fields.Integer(string="Total Mineurs", compute="_get_total_mineurs")
    def _get_total_mineurs(self):
        for rec in self:
            if rec.category == 'D':
                count = self.env['mgp.plainte'].search_count([('tranche_id.name','like','Min')]) 
                rec.total_mineurs = count
            else:
                rec.total_mineurs = 0
    
    total_traites = fields.Integer(string="Total Traités", compute="_get_total_traites")
    def _get_total_traites(self):
        for rec in self:
            if rec.category == 'F':
                count = self.env['mgp.plainte'].search_count([('tranche_id.name','like','Min')]) 
                rec.total_traites = count
            else:
                rec.total_traites = 0

    total_currents = fields.Integer(string="Total En Cours", compute="_get_total_currents")
    def _get_total_currents(self):
        for rec in self:
            if rec.category == 'F':
                count = self.env['mgp.plainte'].search_count([('tranche_id.name','like','Min')]) 
                rec.total_currents = count
            else:
                rec.total_currents = 0

    total_satisfaits = fields.Integer(string="Total Satisfatis", compute="_get_total_satisfaits")
    def _get_total_satisfaits(self):
        for rec in self:
            if rec.category == 'G':
                count = self.env['mgp.plainte'].search_count([('tranche_id.name','like','Min')]) 
                rec.total_satisfaits = count
            else:
                rec.total_satisfaits = 0
    
    total_in_satisfaits = fields.Integer(string="Total Insatisfaits", compute="_get_total_in_satisfaits")
    def _get_total_in_satisfaits(self):
        for rec in self:
            if rec.category == 'H':
                count = self.env['mgp.plainte'].search_count([('tranche_id.name','like','Min')]) 
                rec.total_in_satisfaits = count
            else:
                rec.total_in_satisfaits = 0

    