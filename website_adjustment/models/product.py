# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manual_pdf = fields.Binary(string='Manual pdf', attachment=True)
    manual_pdf_name = fields.Char(string='Manual name')