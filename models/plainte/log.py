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
    ], string='Status', readonly=True, copy=False, default='state')

    group_sender_name = fields.Char("Group", compute="_get_group_sender_name")
    @api.depends('group_sender_id')
    def _get_group_sender_name(self):
        for rec in self:
            if rec.group_sender_id:
                self.group_sender_name = rec.group_sender_id.name

    