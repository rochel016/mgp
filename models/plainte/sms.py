from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Sms(models.Model):
    _name = 'mgp.plainte_sms'
    _description = "Message des plaintes"

    langue = fields.Selection([
        ('MG', 'Malagasy'),
        ('FR', 'Français'),
    ], string="Langue du sms", default="MG")

    statut = fields.Selection([
        ('state', 'Créés par BPO'), # Ticket créé au BPO
        ('state_validate_prea', 'A valider par PREA'), # En validatiton au PREA
        ('state_traitement_pmo', 'A traiter par PMO'), # En traitement ched PMO
        ('state_eval_response_prea', 'A évaluer par PREA'), # EN évaluation chez PREA
        ('state_send_response_bpo', 'A traiter par BPO'), # Donner la réponse au citoyen par BPO
        ('state_done_bpo', 'Tickets traités'), # Le traitment du ticket est terminé
        ('state_invalid', 'Invalides'), # Ticket invalide par le PREA (non exploitable)
        ('state_closed_prea', 'Fermés'), # Ticket fermé par le PREA
    ], string='Statut', copy=False)

    message = fields.Char(string='Message (160 caractères)', required=True)

    # -------------------------------------------------------
    # -------------- Contrainte d'integrité -----------------
    # -------------------------------------------------------
    _sql_constraints = [
        ('name_unique', 
        'unique(langue, statut)',
        'Langue et statut ont déjà un mesage défini')
    ]

    # -------------------------------------------------------
    # ------------------- Contraintes champs ----------------
    # -------------------------------------------------------
    @api.constrains('message')
    def check_message(self):
        """ Le nombre de caractères ne dépasse pas 160 """
        for rec in self:
            if len(rec.message) > 160:
                raise ValidationError(_("Le nombre de caractères ne doit pas dépasser 160"))