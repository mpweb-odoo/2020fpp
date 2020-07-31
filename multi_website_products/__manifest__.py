# -*- coding: utf-8 -*-
{
    'name': 'multi_website_products',
    'version': '1.0.0',
    'summary': 'multi_website_products',
    'description': """
    Make it possible to select on which websites a product should be available
""",
    'depends': [
        'base', 'product', 'website', 'website_sale',
    ],
    'data': [
        # views
        'views/views.xml',
        # datas
        # security
    ],
    'qweb': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
