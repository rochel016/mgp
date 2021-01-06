from odoo import models, fields, api, _, osv
from datetime import datetime
import re  # for matching
from odoo.exceptions import ValidationError
import requests # API curl (SMS tel)

class Plainte(models.Model):
    _name = 'mgp.plainte'
    _description = "Gestion et Suivi des plaintes"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date_appel desc"
    _rec_name = 'reference' # Sur la navigation 

    reference = fields.Char(string="Plainte No", readonly=True, required=True, copy=False, default= 'NOUVEAU')
    date_appel = fields.Datetime(string="Date d'appel", required=True, default=lambda self: fields.datetime.now())
    date_event = fields.Datetime(string="Date d'événement")
    
    # Contact et Localisation
    tel = fields.Char(string="Tél", required=True, copy=False)
    email = fields.Char(string="Email", copy=False)
    langue = fields.Selection([
        ('MG', 'Malagasy'),
        ('FR', 'Français'),
    ], string="Langue du citoyen", default="MG", required=True)

    def _get_default_region(self):
        """
        Revoie la valeur de la region si la commune est definie
        sinon elle reste vide
        Condition: la commune doit exister
        """
        if self.commune_id:
            return self.commune_id.district_id.region_id.id

        return False

    # Localisation : Non stockée dans la base mais juste pour faciliter la recherche de commune (selectoin de dependance)
    region_id = fields.Many2one('mgp.loc_region', store=False, required=True, string="Région", default=_get_default_region)

    
    def _get_default_district(self):
        """
        Revoie la valeur du district si la commune est definie
        sinon elle reste vide
        Condition: la commune doit exister
        """
        if self.commune_id:
            return self.commune_id.district_id
        return False

    # Localisation : Non stockée dans la base mais juste pour faciliter la recherche de commune (selectoin de dependance)
    district_id = fields.Many2one('mgp.loc_district', store=False, required=True, string="District", default=_get_default_district)

    # Localisation à enregistrer (Obligatoire)
    commune_id = fields.Many2one('mgp.loc_commune', ondelete='cascade', string="Commune", required=True)

    # Localisation à enregistrer (Facultative)
    fokontany_id = fields.Many2one('mgp.loc_fokontany', ondelete='cascade', string="Fokontany")

    # Citoyen
    genre = fields.Selection([
        ('feminin', 'Femme'),
        ('masculin', 'Homme'),
    ], string="Genre", required=True)

    tranche_id = fields.Many2one('mgp.citoyen_tranche',
        ondelete='cascade', string="Tranche d'âge", required=True)

    education_id = fields.Many2one('mgp.citoyen_education',
        ondelete='cascade', string="Niveau d'éducation", required=True)

    categorie_id = fields.Many2one('mgp.plainte_categorie_details',
        ondelete='cascade', string="Catégorie", required=True)

    composante_id = fields.Many2one('mgp.plainte_composante',
        ondelete='cascade', string="Composante", required=True)

    ennonce = fields.Text(string="Plainte et Doléance", required=True)

    situation = fields.Selection([
        ('joignable', 'joignable'),
        ('injoignable', 'injoignable'),
    ], string="Situation.", readonly=True)

    resultat = fields.Selection([
        ('satisfait', 'Satisfait'),
        ('insatisfait', 'Insatisfait'),
    ], string="Niveau de satisfaction", readonly=True)

    statut = fields.Selection([
        ('state', 'Créés par BPO'), # Ticket créé au BPO
        ('state_validate_prea', 'A valider par PREA'), # En validatiton au PREA
        ('state_traitement_pmo', 'A traiter par PMO'), # En traitement ched PMO
        ('state_eval_response_prea', 'A évaluer par PREA'), # EN évaluation chez PREA
        ('state_send_response_bpo', 'A traiter par BPO'), # Donner la réponse au citoyen par BPO
        ('state_done_bpo', 'Tickets traités'), # Le traitment du ticket est terminé
        ('state_invalid', 'Invalides'), # Ticket invalide par le PREA (non exploitable)
        ('state_closed_prea', 'Fermés'), # Ticket fermé par le PREA
    ], string='Statut', readonly=True, copy=False, default='state', group_expand='_expand_states')

    def _expand_states(self, states, domain, order):
        """Permet d'afficher tous les status sans (kanban) même si c'est vide"""
        if self.env.user.has_group('mgp.mgp_gouvernance_operateur'):
            return {'state': 'Créés par BPO',
                    'state_send_response_bpo': 'A traiter par BPO',
                    'state_done_bpo': 'Traité'}
        elif self.env.user.has_group('mgp.mgp_gouvernance_prea'):
            return {'state_validate_prea': 'A valider par PREA',
                    'state_traitement_pmo': 'A traiter par PMO',
                    'state_eval_response_prea': 'A évaluer par PREA',
                    'state_send_response_bpo': 'A traiter par BPO',
                    'state_done_bpo': 'Tickéts traités',
                    'state_closed_prea': 'Fermés',
                    'state_invalid': 'Invalide'}
        elif self.env.user.has_group('mgp.mgp_gouvernance_pmo'):
            return {'state_traitement_pmo': 'A traiter par PMO',
                    'state_closed_prea': 'Fermés'}
        else:
            return [key for key, val in type(self).statut.selection]

    # Note: Seul le group 'mgp_gouvernance_prea' a le droit d'ajouter des notes
    note_ids = fields.One2many('mgp.plainte_note', 'plainte_id', string='Notes')

    # Reponses: Seul le group 'mgp_gouvernance_pmo' a le droit d'ajouter des notes
    reponse_ids = fields.One2many('mgp.plainte_reponse', 'plainte_id', string='Réponses')
    
    # Si laréponse est envoyée
    response_complete = fields.Boolean(default=False, string="Réponse complète")

    # L'utilisasteur PMO qui pourrait reçevoir ce ticket (nullable) 
    user_pmo_id = fields.Many2one('res.users', ondelete='cascade', string="User PMO",
        domain=lambda self: [( "groups_id", "=", self.env.ref( "mgp.mgp_gouvernance_pmo" ).id )])

    # -------------------------------------------------------
    # -------------- Contrainte d'integrité -----------------
    # -------------------------------------------------------
    _sql_constraints = [
        ('reference_unique',
        'unique(reference)', # Référence unique
        'La référence doit être unique!')
    ]

    # -------------------------------------------------------
    # -------------- Champs calculé : Status Form -----------
    # -------------------------------------------------------
    statut_display = fields.Text(string="Statut du ticket", compute='get_statut')
    def get_statut(self):
        """ Champs calculé qui renvoie le satut du ticket """
        self.statut_display = dict(self._fields['statut'].selection).get(self.statut)

    statut_response_display = fields.Text(string="Réponse envoyée", compute='check_response')
    def check_response(self):
        """ Renvoie le statut de la réponse"""
        self.statut_response_display = 'Oui' if self.response_complete else 'Non'

    situation_display = fields.Text(string="Situation", compute='get_situation')
    def get_situation(self):
        self.situation_display = dict(self._fields['situation'].selection).get(self.situation)

    result_display = fields.Text(string="Résultat", compute='get_result')
    def get_result(self):
        self.result_display = dict(self._fields['resultat'].selection).get(self.resultat)

    # Liste des logs (AUDIT)
    log_ids = fields.Many2many("mgp.plainte_log", compute="_get_log_ids")
    def _get_log_ids(self):
        for rec in self:
            rec.log_ids = self.env['mgp.plainte_log'].search([('plainte_id','=', rec.id)])
    
    # NAME; Dernier group qui detient le ticket  (Le group receveur)
    actual_group_name = fields.Char(string="Responsable actuel", compute="get_actual_group_name")
    def get_actual_group_name(self):
        for rec in self:
            log = self.env['mgp.plainte_log'].search([('plainte_id','=', rec.id)], order='create_date desc', limit=1)
            if log is not None:
                rec.actual_group_name = log.group_receiver_id.name
                if rec.statut == 'state_traitement_pmo' and self.env.user.has_group('mgp.mgp_gouvernance_prea'):
                    rec.actual_group_name = rec.user_pmo_name # Renvoyer le nol de l'utilisateur du PMO

    # ID: Dernier group qui detient le ticket  (Le group receveur)
    def _get_actual_group_id(self):
        for rec in self:
            log = self.env['mgp.plainte_log'].search([('plainte_id','=', rec.id)], order='create_date desc', limit=1)
            if log is not None:
                return log.group_receiver_id.id

    jours_traitement = fields.Integer(string="Jour(s) de traitement", compute="get_jours_traitement")
    def get_jours_traitement(self):
        """ Renvoie le nombre de jour de traitement du ticket """
        for rec in self:
            import datetime
            d1 = datetime.date(rec.date_appel.year,rec.date_appel.month,rec.date_appel.day)
            d2 = datetime.date.today()
            d3 = d2 - d1
            rec.jours_traitement = d3.days

    zone = fields.Char(compute='_get_localisation')
    def _get_localisation(self):
        """ Renvoie la localisation """
        for rec in self:
            rec.zone = '{} / {}'.format(rec.region_id.name, rec.district_id.name) 
            # rec.zone = '{} / {} / {}'.format(rec.region_id.name, rec.district_id.name, rec.commune_id.name) 
            # if rec.fokontany_id:
            #     rec.zone += ' / {}'.format(rec.fokontany_id.name)

    # -------------------------------------------------------
    # ----------------- GROUP Contraintes -------------------
    # -------------------------------------------------------
    check_write = fields.Boolean(compute='_check_write')
    def _check_write(self):
        """Si la saisie est accessible pour certains group"""
        if self.env.user.has_group('mgp.mgp_gouvernance_prea') \
            or self.env.user.has_group('mgp.mgp_gouvernance_pmo'):
            self.check_write = True
        else:
            self.check_write = False

    check_write_response = fields.Boolean(compute='_check_write_response')
    def _check_write_response(self):
        if self.env.user.has_group('mgp.mgp_gouvernance_operateur') \
            or self.env.user.has_group('mgp.mgp_gouvernance_prea'):
            self.check_write_response = True
        else:
            self.check_write_response = False

    check_write_resultat_situation = fields.Boolean(compute='_check_write_resultat_situation')
    def _check_write_resultat_situation(self):
        """
        Conditions:
        - group is the only operateur
        - user pmo i²s not null
        - statut = invalid
        - last sender group = prea (tester même user) in mgp.plainte_log
        """
        self.check_write_resultat_situation = False
        if self.env.user.has_group('mgp.mgp_gouvernance_operateur') and self.user_pmo_id and self.statut != 'state_invalid':
            # Chercher le dernier log de l'instance en cours
            last_sender = self._get_last_user_sender()
            if last_sender and self.env.uid == last_sender.id and self.response_complete==True:
                self.check_write_resultat_situation = True
            
    is_group_pmo = fields.Boolean(compute='_is_group_pmo')
    def _is_group_pmo(self):
        if self.env.user.has_group('mgp.mgp_gouvernance_pmo'):
            self.is_group_pmo = True
        else:
            self.is_group_pmo = False


    is_reprocessed = fields.Boolean(compute='_is_reprocessed', default=False)
    def _is_reprocessed(self):
        """Si le ticket est retraité => citoyen non satisfait"""
        for rec in self:
            count = 0
            for log in rec.log_ids:
                if log.statut == 'state_eval_response_prea':
                    count += 1
            rec.is_reprocessed = True if count > 1 else False
    
    reprocessed_display = fields.Text(string="Retraitement", compute='get_reprocessed')
    def get_reprocessed(self):
        for rec in self:
            if rec.is_reprocessed:
                rec.reprocessed_display = 'Ticket en'
            else:
                rec.reprocessed_display = ''

    # -------------------------------------------------------
    # ------------------- Contraintes champs ----------------
    # -------------------------------------------------------
    @api.constrains('tel')
    def check_tel(self):
        """ Le téléphone ne contient que des chiffres, séparé par point virgule """
        for rec in self:
            if len(rec.tel) != 10 or not re.match(r"^[0-9;]+$", rec.tel):
                raise ValidationError(_("Le numéro doit être de 10 chiffres"))
                # ??? return {
                #     'type': 'ir.actions.client',
                #     'tag': 'display_notification',
                #     'params': {
                #         'title': _('Envoi du ticket au PREA'),
                #         'message': _("Le ticket n° a été envoyée aux admin PREA."),
                #         'type':'success',  
                #         'sticky': False,
                #     },
                # }

    @api.constrains('ennonce')
    def check_ennonce(self):
        """ 10 nombre digits """
        for rec in self:
            if len(rec.ennonce) < 10:
                # ??? return {
                #     'type': 'ir.actions.client',
                #     'tag': 'display_notification',
                #     'params': {
                #         'title': _('Envoi du ticket au PREA'),
                #         'message': _("Le ticket n° a été envoyée aux admin PREA."),
                #         'type':'success',  
                #         'sticky': False,
                #     },
                # }
                raise ValidationError(_("L'ennoncé de la plainte doît contenir au moins 10 caractères"))

    # -------------------------------------------------------
    # ----- Localisation : Automatisation des dropdown ------
    # -------------------------------------------------------
    @api.onchange('region_id')
    def _onchange_region_id(self):
        if self.region_id:
            self.district_id = False # Blank field
            self.district_id = 0 # Empty value field

            self.commune_id = False # Blank field
            self.commune_id = 0 # Empty value field

            # Fill district_id (magie)
            return {'domain': {'district_id': [('region_id', '=',self.region_id.id)]}}

    @api.onchange('district_id')
    def _onchange_district_id(self):
        if self.district_id:
            self.commune_id = False # Blank field
            self.commune_id = 0 # Empty value field

            # Fill commune_id
            return {'domain': {'commune_id': [('district_id', '=',self.district_id.id)]}}

    @api.onchange('commune_id')
    def _onchange_commune_id(self):
        if self.commune_id:
            self.fokontany_id = False # Blank field
            self.fokontany_id = 0 # Empty value field

            # Fill commune_id
            return {'domain': {'fokontany_id': [('commune_id', '=',self.commune_id.id)]}}

    # -------------------------------------------------------
    # -------------------- Créer log  -----------------------
    # -------------------------------------------------------
    def _do_log(self, plainte_id, group_sender_id, group_receiver_id, action, statut, notif_sender, notif_receiver):
        """
        Créer le journal(log) à chaque action sur un ticket(plainte)
        """
        self.env['mgp.plainte_log'].create({
            'plainte_id': plainte_id,
            'action': action,
            'statut': statut,
            'group_sender_id': group_sender_id,
            'group_receiver_id': group_receiver_id,
            'notif_sender': notif_sender,
            'notif_receiver': notif_receiver
        })

    # -------------------------------------------------------
    # -------------------- Créer note -----------------------
    # -------------------------------------------------------
    def send_note(self, plainte_id, note):
        """
        Créer une note associée à un ticket
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_prea'):
            self.env['mgp.plainte_note'].create({
                'plainte_id': plainte_id,
                'note': note
            })
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Envoi de note"),
                    'message': _("Seul l'admin PREA peut envoyer une note."),
                    'type':'danger',  
                    'sticky': False,
                },
            }

    # -------------------------------------------------------
    # --------------- Workflow : BPO ACTIONS ----------------
    # -------------------------------------------------------
    @api.model
    def create(self, vals):
        """
        - User : BPO Operator
        - Status: 'state"
        - Desc: Créer le ticket
        - By BPO
        - Remarque: Référence auto-incrémenté et First Workflow
        """

        # 1 GET YOUR SEQUENCE WITH LATEST INCREMENT RUNNING NUMBER
        seq = self.env['ir.sequence'].next_by_code('mgp.plainte') or 'NOUVEAU'

        # 2 SET THE SEQUENCE ON 'NAME' FIELD
        vals['reference'] = seq

        # 3 RETURN SUPER TO EXTEND THE CREATE METHOD 
        record = super(Plainte, self).create(vals)

        # 4 - Log : après la création d'un nouveau ticket
        self._do_log(
            plainte_id = record.id, 
            group_sender_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
            group_receiver_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
            action = "Création d'un nouveau ticket",
            statut = "state",
            notif_sender = "Ticket créé",
            notif_receiver = "Ticket n° {} en attente d'envoi au PREA".format(record.reference))

        # 5 - Envoyer un SMS Phone au citoyen
        # status_code = self.send_sms_via_orange(
        #     adresse = record.tel[1:], # les 9 derniers chiffres uniquement
        #     senderAddress = '320450952',
        #     message = 'Votre ticket n° {} a été créé le {}'.format(record.reference, record.create_date.strftime("%d/%m/%Y, %H:%M:%S")))
        
        #if status_code in (200)


        return record

    def unlink(self):
        """
        Surcharge de la méthode "Suppression" d'un ticket
        """
        resp_group_id = self._get_actual_group_id()
        current_group_id = self.env.ref('mgp.mgp_gouvernance_operateur').id
        
        if self.statut == 'state' and resp_group_id == current_group_id:
            return super(Plainte, self).unlink()
        else:
            raise ValidationError(_("Le ticket n° {} ne peut plus être supprimé.".format(self.reference)))
            # ???
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'title': 'Création du ticket',
            #         'message': "Le ticket n° {} ne peut plus être supprimé.".format(self.reference),
            #         'type':'danger',  
            #         'sticky': False,
            #     },
            # }

    def action_send_to_prea(self):
        """
        - User : BPO Operator
        - Status: 'state_validate_prea"
        - Desc: Envoyer le ticket aux admin PREA
        - From BPO to PREA
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_operateur'):
            for rec in self:
                # 1 - Update ticket state
                rec.statut = 'state_validate_prea'
            
                # 2 - Log : Envoi du ticket au PREA
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    action = "Envoi du ticket aux admin PREA",
                    statut = "state_validate_prea",
                    notif_sender = "Ticket envoyée au PREA",
                    notif_receiver = "Ticket n° {} en attente de validation".format(rec.reference))
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Envoi du ticket au PREA"),
                    'message': _("Seul l'opérateur BPO peut envoyer ce ticket au PREA."),
                    'type':'danger',  
                    'sticky': False,
                },
            }

    def action_joignable(self):
        """
        - User : BPO
        - Status: 'state_send_response_bpo', Statut non traité, attends la satisfaction ou non
        - situation = 'joignable'
        - Desc: Le ticket est résolu
        - From BPO to PREA
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_operateur'):
            for rec in self:
                # 1 - Update ticket state
                rec.statut = 'state_send_response_bpo'
                rec.situation = 'joignable'
            
                # 2 - Log : Citoyen joignable
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    action = "Joindre le citoyen",
                    statut = "state_send_response_bpo",
                    notif_sender = "Citoyen joignable",
                    notif_receiver = "Le citoyen est joignable pour le ticket n° {}".format(rec.reference))
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Joindre le citoyen"),
                    'message': _("Seul l'opérateur BPO peut faire cette action."),
                    'type':'danger',  
                    'sticky': False,
                },
            }
    
    def action_injoignable(self):
        """
        - User : BPO
        - Status: 'state_done_bpo' # Ce statut est traité
        - Situation= 'injoignable'
        - Desc: Le citoyen est injoignable
        - From BPO to PREA
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_operateur'):
            for rec in self:
                # 1 - Update ticket state
                rec.statut = 'state_done_bpo'
                rec.situation = 'injoignable'
            
                # 2 - Log : citoyen injoignable
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    action = "Joindre le citoyen",
                    statut = "state_done_bpo",
                    notif_sender = "Citoyen injoignable",
                    notif_receiver = "Le citoyen est injoignable")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Appel injoignable"),
                    'message': _("Seul l'opérateur BPO peut faire cette action."),
                    'type':'danger',  
                    'sticky': False,
                },
            }

    def action_satisfait(self):
        """
        - User : BPO
        - Status: 'state_done_bpo' # Le ticket est traité
        - resultat: 'satisfait'
        - Desc: Le citoyen est satisfait
        - From BPO to PREA
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_operateur'):
            for rec in self:
                # 1 - Update ticket state
                rec.statut = 'state_done_bpo'
                rec.resultat = 'satisfait'
            
                # 2 - Log : citoyen satisfait
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    action = "Réponse du client",
                    statut = "state_done_bpo",
                    notif_sender = "Citoyen satisfait",
                    notif_receiver = "Le citoyen est satisfait")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Réponse du client"),
                    'message': _("Seul l'opérateur BPO peut faire cette action."),
                    'type':'danger',  
                    'sticky': False,
                },
            }
    
    def action_non_satisfait(self):
        """
        - User : BPO
        - Status: 'state_eval_response_prea' # Le tiocket va retourner chez le PREA pour reevalaluation
        - resultat= 'insatisfait'
        - Desc: Renvoi du tocket au PREA
        - From BPO to PREA
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_operateur'):
            for rec in self:
                # 1 - Update ticket state
                rec.statut = 'state_validate_prea'
                rec.resultat = None # TRES IMPORTANT
                rec.response_complete = False # TRES IMPORTANT
                rec.situation = None # TRES IMPORTANT
            
                # 2 - Log : Renvoi du ticket au PREA
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    action = "Renvoi du ticket au PREA (insatisfaction)",
                    statut = "state_eval_response_prea",
                    notif_sender = "Ticket renvoyé au PREA pour retraitement",
                    notif_receiver = "Le ticket est renvoyé pour retraitement au niveau du PMO")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Renvoi du ticket au PREA"),
                    'message': _("Seul l'opérateur BPO peut faire cette action."),
                    'type':'danger',
                    'sticky': False,
                },
            }

    # -------------------------------------------------------
    # --------------- Workflow : PREA ACTIONS ---------------
    # -------------------------------------------------------
    def action_cancel(self):
        """
        - User : Admin PREA 
        - Status: 'state_invalid'
        - Desc: Annuler le ticket (le rendre 'non valide')
        - From PREA to PMO
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_prea'):
            for rec in self:
                # 1 - Update ticket state
                rec.statut = 'state_invalid'

                # 2 - Log : Annuler le ticket (le ticket devient invalide)
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    action = "Annulation du ticket",
                    statut = "state_invalid",
                    notif_sender = "Ticket annulé",
                    notif_receiver = "Ticket annulé par PREA")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Annulation du ticket"),
                    'message': _("Seul l'admin PREA peut annuler ce ticket."),
                    'type':'danger',  
                    'sticky': False,
                },
            }
        
    def action_send_to_pmo(self):
        """
        - User : Admin PREA
        - Status: 'state_traitement_pmo'
        - Desc: Envoyer le ticket au PMO
        - From PREA to PMO
        """
        if self.user_pmo_id.id == False:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Envoi ticket au PMO"),
                    'message': _("Veuillez seléctionner un utilisateur PMO."),
                    'type':'danger',
                    'sticky': False,
                },
            }
        elif self.env.user.has_group('mgp.mgp_gouvernance_prea'):
            for rec in self:
                # 1 - Update ticket state
                rec.statut = 'state_traitement_pmo'

                # 2 - Log : Envoi du ticket au PMO
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_pmo').id,
                    action = "Envoi du ticket au PMO ({})".format(rec.user_pmo_id.name),
                    statut = "state_traitement_pmo",
                    notif_sender = "Ticket envoyé au PMO",
                    notif_receiver = "Ticket reçu du PREA")
                
                # 3 - Envoyer un sms au citoyen pour info que le ticket est déjà en traitement
                # ???
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Envoi ticket au PMO"),
                    'message': _("Seul l'admin PREA peut envoyer ce ticket au PMO."),
                    'type':'danger',  
                    'sticky': False,
                },
            }

    def action_send_response_to_bpo(self):
        """
        - User : PREA
        - Status: 'state_send_response_bpo'
        - Desc: Envoyer la réponse au BPO
        - From PREA Tto BPO
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_prea'):
            for rec in self:
                if not rec.reponse_ids:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _("Envoi réponse"),
                            'message': _("Vous dévez saisir la réponse à envoyer."),
                            'type':'danger',  
                            'sticky': False,
                        },
                    }

                # 1 - Update ticket state
                rec.statut = 'state_send_response_bpo'
                rec.response_complete = True
            
                # 2 - Log : Envoi réponse
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
                    action = "Envoi de réponse au BPO",
                    statut = "state_send_response_bpo",
                    notif_sender = "Réponse envoyée au BPO",
                    notif_receiver = "Réponse reçue du PREA")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Envoi réponse"),
                    'message': _("Seul l'admin PREA peut envoyer cette réponse au BPO."),
                    'type':'danger',  
                    'sticky': False,
                },
            }
    
    def action_close(self):
        """
        - User : PREA
        - Status: 'state_closed_prea' # Ce statut ne change pas mais reste 'done'
        - Desc: Fermer le ticket (plainte)
        - From PREA to BPO
        - Conditions supplémentaire: valid si 'injoignable' ou 'satisfait' ou 'insatisfait'
        """
        if self.env.user.has_group('mgp.mgp_gouvernance_prea') \
            and (self.situation=='injoignable' or self.resultat=='satisfait'):
            for rec in self:
                # 1 - Update ticket state
                rec.statut = 'state_closed_prea'
            
                # 2 - Log : Fermer le ticket
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_prea').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_operateur').id,
                    action = "Fermeture du ticket",
                    statut = "state_closed_prea",
                    notif_sender = "Ticket fermé",
                    notif_receiver = "Le ticket est fermé")
        else:
            message = ''
            if (self.situation!='injoignable' or self.resultat!='satisfat'):
                message = "Impossible de fermer le ticket que lorsqu'il est injoignable ou bien satisfait"
            else:
                message = "Seul l'administrateur PREA peut fermer un ticket."
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Fermeture du ticket"),
                    'message': _(message),
                    'type':'danger',  
                    'sticky': False,
                },
            }
    
    #-----------------------------------------------------------
    #-------------------- Workflow ACTIONS PMO -----------------
    #-----------------------------------------------------------
    def action_send_response_to_prea(self):
        """
        - User : PMO
        - Status: 'state_eval_response_prea'
        - Desc: Envoyer la réponse au PREA
        - From PMO to PREA
        """
        if not self.response_complete:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Envoi réponse au PREA"),
                        'message': _("Vous devez cocher <si réponse complète> et sauvegarder le ticket avant d'éffectuer cette opération"),
                        'type':'danger',  
                        'sticky': False,
                    },
                }

        if not self.reponse_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Envoi réponse au PREA"),
                    'message': _("Vous devez saisir la réponse à envoyer."),
                    'type':'danger',  
                    'sticky': False,
                },
            }

        if self.env.user.has_group('mgp.mgp_gouvernance_pmo'):
            for rec in self:
                if not rec.reponse_ids:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _("Envoi réponse"),
                            'message': _("Vous dévez saisir la réponse à envoyer."),
                            'type':'danger',  
                            'sticky': False,
                        },
                    }

                # 1 - Update ticket state and response
                rec.statut = 'state_eval_response_prea'
                rec.response_complete = True
            
                # 2 - Log : Envoi réponse
                self._do_log(
                    plainte_id = rec.id,
                    group_sender_id = self.env.ref('mgp.mgp_gouvernance_pmo').id,
                    group_receiver_id = self.env.ref('mgp.mgp_gouvernance_prea').id, # Traitement fini
                    action = "Envoi de réponse au PREA",
                    statut = "state_eval_response_prea",
                    notif_sender = "Réponse envoyée au PREA",
                    notif_receiver = "Réponse reçue du PMO")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Envoi réponse"),
                    'message': _("Seul l'utilisateur PMO peut envoyer cette réponse au PREA."),
                    'type':'danger',  
                    'sticky': False,
                },
            }

    # -------------------------------------------------------
    # ---------------------- User : Group -------------------
    # -------------------------------------------------------
    def _get_groups_from_user(self, user_id):
        """
        Get group ids from user
        Return a list of groups ids
        """
        groups_ids = []
        self.env.cr.execute("SELECT gid FROM res_groups_users_rel WHERE uid="+str(user_id))
        res = self.env.cr.fetchall()
        for group_id in res:
            groups_ids.append(group_id[0])
        return groups_ids

    # Le dernier user qui a envoyée ce ticket
    def _get_last_user_sender(self):
        """
        get the last user sender in log
        """
        for rec in self:
            log = self.env['mgp.plainte_log'].search([('plainte_id','=', rec.id)], order='create_date desc', limit=1)
            if log is not None:
                return log.create_uid
        return None

    # Le dernier group qui a envoyée ce ticket
    def _get_last_group_sender(self):
        """
        get the last group sender in log
        """
        for rec in self:
            log = self.env['mgp.plainte_log'].search([('plainte_id','=', rec.id)], order='create_date desc', limit=1)
            if log is not None:
                return log.group_sender_id
        return None

    # Le dernier group qui a reçu ce ticket
    is_last_group_receiver = fields.Boolean(compute='_is_last_group_receiver')
    def _is_last_group_receiver(self):
        """
        if the group of current user is the last receiver in log
        """
        # Dernier group receiver
        group_receiver_id = self._get_actual_group_id()

        # Group du current user
        groups_ids = self._get_groups_from_user(self.env.uid)
        
        #Check if group receiver of current user 
        if group_receiver_id in groups_ids:
            self.is_last_group_receiver = True
        else:
            self.is_last_group_receiver = False
    
    # -------------------------------------------------------
    # ---------- Assigner ticket à un user du PMO -----------
    # -------------------------------------------------------
    def assigner_tiket_user_pmo(self):
        title = 'Assigner le ticket n°{} à un utilisateur du PMO'.format(self.reference)
        if self.user_pmo_id:
            title = "Re-assigner le ticket n°{} à ".format(self.reference)

        return {
            'name': title,
            'res_model':'mgp.plainte',
            'view_mode':'form',
            'res_id':self.id,
            'type':'ir.actions.act_window',
            'view_id':self.env.ref('mgp.select_pmo_form_view').id, 
            'target':'new',
            'flags': {'initial_mode': 'edit'},  
        }

    # User PMO qui traite le dossier
    user_pmo_name = fields.Char(compute='_get_user_pmo_name')
    def _get_user_pmo_name(self):
        for rec in self:
            if rec.user_pmo_id:
                res = self.env['res.users'].search([('id', '=', rec.user_pmo_id.id)])
                self.user_pmo_name = res.name
            else:
                self.user_pmo_name = ''


    # -------------------------------------------------------
    # ------------- Gestion de SMS téléphonique -------------
    # -------------------------------------------------------
    """
    curl -X POST -H "Authorization: Bearer XbwTrHQeljjEhTOVhXS2yVJFwH3G" -H "Content-Type: application/json" 
    -d '{"outboundSMSMessageRequest":{"address": "tel:+261349477494", 
    "senderAddress":"tel:+2613 20450952",
    "outboundSMSTextMessage":{"message": "Hi Odoo Master, mety ito e"}}}' 
    "https://api.orange.com/smsmessaging/v1/outbound/tel%3A%2B261320450952/requests"
    """
    def send_sms_via_orange(self, address="", senderAddress="", message=""):
        """
        Desc: Envoyer un sms au citoyen 
        @address: adresse du destinataire (citoyen), ex:320000000, 330000000, 340000000
        @senderAddress: adresse de l'envoyeur, ex: 320450952
        @message; message à envoyer
        Note: Le format du telephone 9 digits sans le +261
        """
        headers = {
            'Authorization': 'Bearer XbwTrHQeljjEhTOVhXS2yVJFwH3G',
            'Content-Type': 'application/json',
        }

        data = '{"outboundSMSMessageRequest": {"address": "tel:+261%s","senderAddress":"tel:+261%s","outboundSMSTextMessage":{"message": "%s"}}}' % (address, senderAddress, message)

        response = requests.post('https://api.orange.com/smsmessaging/v1/outbound/tel%3A%2B261{}/requests'.format(senderAddress), headers=headers, data=data)

        print('-----------------')
        print(response.status_code)
        return response.status_code

        # Paramétrer le sms à envoyer
        # Sauvegarder le sms envoyé


    # -------------------------------------------------------
    # --------------- Gestion de MAIL personna --------------
    # -------------------------------------------------------
    def _send_email(self, user_id):
        temp = self.env.ref('mgp.mgp_email_template')
        if temp:
            # example: user - instance of res.users
            temp.sudo().with_context().send_mail(user_id, force_send=True)

    @api.model
    def send_email_prea_job(self):
        print("Sending email to RPEA users at {}".format(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
        self.env.cr.execute("SELECT uid FROM res_groups_users_rel WHERE gid = {}".format(self.env.ref( "mgp.mgp_gouvernance_prea" ).id))
        users_pmo_ids = self.env.cr.fetchall()
        
        for user_id in users_pmo_ids:
            self._send_email(user_id[0])

    @api.model
    def send_email_pmo_job(self):
        print("Sending email to RMO users at {}".format(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
        self.env.cr.execute("SELECT uid FROM res_groups_users_rel WHERE gid = {}".format(self.env.ref( "mgp.mgp_gouvernance_pmo" ).id))
        users_pmo_ids = self.env.cr.fetchall()
        
        for user_id in users_pmo_ids:
            self._send_email(user_id[0])


    # -------------------------------------------------------
    # --------------- Controle CRUD with status -------------
    # -------------------------------------------------------
    x_css = fields.Html(
        string='CSS',
        sanitize=False,
        compute='_compute_css',
        store=False,
    )
    #@api.depends('statut')
    def _compute_css(self):
        for res in self:
            res.x_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            # if res.statut in ('state_validate_prea', 'state_eval_response_prea', 'state_invalid'):
            #     print(res.statut)
            #     res.x_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            # else:
            #     res.x_css = False

    # ('state', 'Créés par BPO'), # Ticket créé au BPO
    # ('state_validate_prea', 'A valider par PREA'), # En validatiton au PREA
    # ('state_traitement_pmo', 'A traiter par PMO'), # En traitement ched PMO
    # ('state_eval_response_prea', 'A évaluer par PREA'), # EN évaluation chez PREA
    # ('state_send_response_bpo', 'A traiter par BPO'), # Donner la réponse au citoyen par BPO
    # ('state_done_bpo', 'Tickets traités'), # Le traitment du ticket est terminé
    # ('state_invalid', 'Invalides'), # Ticket invalide par le PREA (non exploitable)
    # ('state_closed_prea', 'Fermés'), #
