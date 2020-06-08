# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    website_ids = fields.Many2many('website', string="Multiple Websites")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_ids = fields.Many2many('website', string="Multiple Websites")


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    website_ids = fields.Many2many('website', string="Multiple Websites")

    @api.multi
    def _is_available_on_website(self, website_id):
        """ To be able to be used on a website, a pricelist should either:
        - Have its `website_id` set to current website (specific pricelist).
        - Have no `website_id` set and should be `selectable` (generic pricelist)
          or should have a `code` (generic promotion).

        Note: A pricelist without a website_id, not selectable and without a
              code is a backend pricelist.

        Change in this method should be reflected in `_get_website_pricelists_domain`.
        """
        self.ensure_one()
        return website_id in self.website_ids.mapped('id') or (not self.website_id and (self.selectable or self.sudo().code))
