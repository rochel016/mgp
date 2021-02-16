from odoo import http
from odoo.http import request

"""
REST API CITOYENS
"""
class CitoyenController(http.Controller):
    @http.route(['/educations', '/educations/<int:id>'], type='json', auth="none")
    def get_educations(self, id=None):
        if id:
            domain = [('id', '=', id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.citoyen_education'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name
            })
        return res

class CitoyenController(http.Controller):
    @http.route(['/tranches', '/tranches/<int:id>'], type='json', auth="none")
    def get_tranches(self, id=None):
        if id:
            domain = [('id', '=', id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.citoyen_tranche'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name
            })
        return res

        