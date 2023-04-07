from requests.sessions import default_headers
from odoo import models, fields, api
from datetime import datetime

class Log(models.Model):
    _name = 'mgp.plainte_log'
    _description = "Log des plaintes"
    _order = "plainte_id asc"

    plainte_id = fields.Many2one('mgp.plainte', ondelete='cascade', string="Plainte", required=True)
    action = fields.Char(string="Action", required=True)
    group_sender_id = fields.Many2one('res.groups', ondelete='cascade', string="Group Sender", required=True)
    group_receiver_id = fields.Many2one('res.groups', ondelete='cascade', string="Group Receiver", required=True)
    notif_sender = fields.Char(string="Notification de l'envoyeur")
    notif_receiver = fields.Char(string="Notification du recepteur")
    statut = fields.Selection([
        ('state', 'Créé par BPO'), # Ticket créé au BPO
        ('state_validate_prea', 'A valider par PREA'), # En validatiton au PREA
        ('state_traitement_pmo', 'A traiter par PMO'), # En traitement ched PMO
        ('state_eval_response_prea', 'A évaluer par PREA'), # EN évaluation chez PREA
        ('state_send_response_bpo', 'A traiter par BPO'), # Donner la réponse au citoyen par BPO
        ('state_done_bpo', 'Traité'), # Le traitment du ticket est terminé
        ('state_invalid', 'Invalide'), # Ticket invalide par le PREA (non exploitable)
        ('state_closed_prea', 'Fermé'), # Ticket fermé par le PREA
        ('state_call_back_success', 'Appel citoyen réussi'),
        ('state_call_back_error', 'Appel citoyen non abouti'),
    ], string='Status', readonly=True, copy=False, default='state')
    
    # Message envoyé au citoyen (160 caractère)
    sms = fields.Char(string="Message envoyé", size=160)
    sms_sent = fields.Boolean(string="Si message envoyé", default=False)
