from odoo import models, fields
from datetime import datetime

class Note(models.Model):
    _name = 'mgp.plainte_note'
    _description = "Notes des plaintes"
    _order = "plainte_id asc"

    plainte_id = fields.Many2one('mgp.plainte', ondelete='cascade', string="Plainte", required=True)
    note = fields.Char(string='Note', required=True)
    
    # attached file for each note
    upload_file = fields.Binary(string="Fichier")
    file_name = fields.Char(string="Nom du fichier")