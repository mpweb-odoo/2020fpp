# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController
from odoo.http import request

class WebsiteSale(ProductConfiguratorController):
    def _get_search_domain(self, search, category, attrib_values):
        res = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)
        res.append(('website_ids', 'in', (request.website.get_current_website().id)))
        return res
