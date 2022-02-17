from odoo import http
from odoo.http import request

"""
REST API LOCALIZATIONS
"""
class LocalizationController(http.Controller):
    @http.route(['/provinces', '/provinces/<int:id>'], type='json', auth="none")
    def get_provinces(self, id=None):
        if id:
            domain = [('id', '=', id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.loc_province'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name
            })
        return res
    
    @http.route(['/regions', '/regions/<int:id>', '/regions/province/<int:province_id>'], type='json', auth="none")
    def get_regions(self, id=None, province_id=None):
        if id:
            domain = [('id', '=', id)]
        elif province_id:
            domain = [('province_id', '=', province_id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.loc_region'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name,
                "province_id": o.province_id.id
            })
        return res
    
    @http.route(['/districts', '/districts/<int:id>', '/districts/region/<int:region_id>'], type='json', auth="none")
    def get_districts(self, id=None, region_id=None):
        if id:
            domain = [('id', '=', id)]
        elif region_id:
            domain = [('region_id', '=', region_id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.loc_district'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name,
                "region_id": o.region_id.id
            })
        return res
    
    @http.route(['/communes', '/communes/<int:id>', '/communes/district/<int:district_id>'], type='json', auth="none")
    def get_communes(self, id=None, district_id=None):
        if id:
            domain = [('id', '=', id)]
        elif district_id:
            domain = [('district_id', '=', district_id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.loc_commune'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name,
                "district_id": o.district_id.id
            })
        return res
    
    @http.route(['/fokontany', '/fokontany/<int:id>', '/fokontany/commune/<int:commune_id>'], type='json', auth="none")
    def get_fokontany(self, id=None, commune_id=None):
        if id:
            domain = [('id', '=', id)]
        elif commune_id:
            domain = [('commune_id', '=', commune_id)]
        else:
            domain = []
        res = []
        data = request.env['mgp.loc_fokontany'].search(domain)
        for o in data:
            res.append({
                "id": o.id,
                "name": o.name,
                "commune_id": o.commune_id.id
            })
        return res