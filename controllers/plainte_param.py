from odoo import http
from odoo.http import request

"""
REST API PLAINTES PARAMS
"""
class PlainteParamController(http.Controller):
    @http.route(['/composantes', '/composantes/<int:id>'], type='json', auth="none")
    def get_composantes(self, id=None):
        if id:
            domain = [('id', '=', id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.plainte_composante'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name
            })
        return res
    
    @http.route(['/categories', '/categories/<int:id>'], type='json', auth="none")
    def get_categories(self, id=None):
        if id:
            domain = [('id', '=', id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.plainte_categorie'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name
            })
        return res
    
    @http.route(['/categorie_details', '/categorie_details/<int:id>', '/categorie_details/categorie/<int:categorie_id>'], type='json', auth="none")
    def get_categorie_details(self, id=None, categorie_id=None):
        if id:
            domain = [('id', '=', id)]
        elif categorie_id:
            domain = [('categorie_id', '=', categorie_id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.plainte_categorie_details'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name,
                "categorie_id": o.categorie_id.id
            })
        return res
    
    