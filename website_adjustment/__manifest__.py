# -*- coding: utf-8 -*-
{
    'name': "wfp_website_adjustment",

    'summary': """
        Adjustment of website: display products in categories""",

    'description': """
        They sell a lot of mechanical products. Their database will have to start with 74000 products and it will be more and more.
        On the ecommerce they need to display a variety of different categories with many subcategories.
        Therefore they need some changes in order to be smooth.
    """,

    'author': "Odoo sa",
    'website': "http://www.odoo.com",

    'category': 'website',
    'version': '0.1',

    'depends': [
        'website',
        'website_sale',
        'sale',
        'sale_management',
        'stock',
    ],

    'data': [
        'views/product_template.xml',
        'views/templates.xml',
    ]
}
