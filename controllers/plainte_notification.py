# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class PlainteNotification(http.Controller):
    """
    Permet le renvoi les tickets à traiter de l'user en cours (nombre / liste)
    """
    @http.route(['/plainte_notif'], type='json', auth="user", website=True)
    def plainte_notif(self, **post):
        # Chercher les dernier log des plaintes (plaintes != state_invalid ou state_closed_prea)
        
        current_group_id = 0
        sql_count = None
        sql_count_partial = ''
        sql_tickets = ''
        
        if request.env.user.has_group('mgp.mgp_gouvernance_operateur'):
            current_group_id = request.env.ref('mgp.mgp_gouvernance_operateur').id 
            sql_count_partial = "('state', 'state_send_response_bpo')"

        elif request.env.user.has_group('mgp.mgp_gouvernance_prea'):
            current_group_id = request.env.ref('mgp.mgp_gouvernance_prea').id 
            sql_count_partial = "('state_validate_prea', 'state_eval_response_prea', 'state_done_bpo')"

        elif request.env.user.has_group('mgp.mgp_gouvernance_pmo'):
            current_group_id = request.env.ref('mgp.mgp_gouvernance_pmo').id
            sql_count_partial = "('state_traitement_pmo')"
            sql_count = """select count(*) from mgp_plainte
                where id in (select plainte_id from mgp_plainte_log
                where id in (select max(id) from mgp_plainte_log group by plainte_id)
                and statut in {}
                and group_receiver_id = {})
                and user_pmo_id =  {}""".format(sql_count_partial, current_group_id, request.uid) # User PMO
            
            sql_tickets = """select mgp_plainte.reference, mgp_plainte_log.notif_receiver from mgp_plainte_log
                inner join mgp_plainte on mgp_plainte.id = mgp_plainte_log.plainte_id 
                where mgp_plainte_log.id in (select max(id) from mgp_plainte_log group by plainte_id)
                and mgp_plainte_log.statut in {}
                and mgp_plainte_log.group_receiver_id = {}
                and mgp_plainte.user_pmo_id = {}""".format(sql_count_partial, current_group_id, request.uid) # User PMO
        
        else:
            # Autre user group comme Admin
            return {
                'count' : '',
                'tickets' : ''
            }
        
        if not sql_count:
            # BPO ou PREA
            sql_count = """ select count(*) from mgp_plainte_log
                where id in (select max(id) from mgp_plainte_log group by plainte_id)
                and statut in {} and group_receiver_id = {};""".format(sql_count_partial, current_group_id)
            
            sql_tickets = """select mgp_plainte.reference, mgp_plainte_log.notif_receiver from mgp_plainte_log
                inner join mgp_plainte on mgp_plainte_log.plainte_id = mgp_plainte.id
                where mgp_plainte_log.id in (select max(id) from mgp_plainte_log group by plainte_id)
                and mgp_plainte_log.statut in {}
                and mgp_plainte_log.group_receiver_id = {}""".format(sql_count_partial, current_group_id)

        # COUNT
        request.env.cr.execute(sql_count)
        res = request.env.cr.dictfetchall() # Format dictionnary; fetchall Format List of tuple [(val1,val2,...)]
        count = res[0]['count']
        if count == 0:
            count = ''

        # LISTE
        tickets = None
        if sql_tickets:
            request.env.cr.execute(sql_tickets)
            tickets = request.env.cr.fetchall()

        return {
            'count' : count,
            'tickets' : tickets
        }