# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    manual_pdf = fields.Binary(string='Manual pdf', attachment=True)
    manual_pdf_name = fields.Char(string='Manual name')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manual_pdf = fields.Binary(string='Manual pdf', attachment=True)
    manual_pdf_name = fields.Char(string='Manual name')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    image_medium = fields.Binary("Medium-sized image", attachment=True)


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    website_size_x = fields.Integer('Size X', default=1)
    website_size_y = fields.Integer('Size Y', default=1)
    website_style_ids = fields.Many2many('product.style', string='Styles')
    website_published = fields.Boolean(default=True)