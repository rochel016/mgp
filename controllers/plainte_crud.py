from odoo import http
from odoo.http import request

"""
REST API CITOYENS
"""
class TicketController(http.Controller):
    @http.route(['/create_ticket'], type="json", auth="public")
    def create_ticket(self, **rec):
        if request.jsonrequest:
            if rec:
                vals = {
                    'date_appel': rec ['date_appel'],
                    'date_event': rec ['date_event'],
                    'tel': rec ['tel'],
                    'email': rec ['email'],
                    'langue': rec ['langue'],
                    'commune_id': rec ['commune_id'],
                    'fokontany_id': rec ['fokontany_id'],
                    'genre': rec ['genre'],
                    'tranche_id': rec ['tranche_id'],
                    'education_id': rec ['education_id'],
                    'categorie_id': rec ['categorie_id'],
                    'composante_id': rec ['composante_id'],
                    'ennonce': rec ['ennonce']
                }
                #  - Create a new ticket
                new = request.env["mgp.plainte"].sudo().create(vals)
                args = {'success': True, 'message': 'Success', 'Ticket': new.reference}

        return args