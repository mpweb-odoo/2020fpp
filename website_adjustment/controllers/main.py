import base64
import logging
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import TableCompute

from odoo.exceptions import UserError, AccessError
from odoo.exceptions import MissingError
from odoo import fields, http, tools, _
from odoo.http import request, content_disposition
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL

_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

class WebsiteSaleProductCategories(WebsiteSale):

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        domain = self._get_search_domain(search, category, attrib_values)
        Product = request.env['product.template'].with_context(bin_size=True)
        Category = request.env['product.public.category']
        search_product = Product.search(domain)
        if search:
            categories = search_product.mapped('public_categ_ids')
            search_categories = Category.search(
                [('id', 'parent_of', categories.ids)] + request.website.website_domain())
            categs = search_categories.filtered(lambda c: not c.parent_id)
        else:
            categs = Category.search([('parent_id', '=', False)] + request.website.website_domain())

        if category:
            categs = category.child_id
        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))

        values = {
            'search': search,
            'category': category,
            'categories': categs,
            'keep': keep,
        }

        if not category or category.child_id:
            return request.render("website_adjustment.product_categories_shop_view", values)

        else:
            add_qty = int(post.get('add_qty', 1))
            if category:
                category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
                if not category or not category.can_access_from_current_website():
                    raise NotFound()

            if ppg:
                try:
                    ppg = int(ppg)
                except ValueError:
                    ppg = PPG
                post["ppg"] = ppg
            else:
                ppg = PPG

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}

            domain = self._get_search_domain(search, category, attrib_values)

            keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                            order=post.get('order'))

            pricelist_context, pricelist = self._get_pricelist_context()

            request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

            url = "/shop"
            if search:
                post["search"] = search
            if attrib_list:
                post['attrib'] = attrib_list

            Product = request.env['product.template'].with_context(bin_size=True)

            Category = request.env['product.public.category']
            search_categories = False
            search_product = Product.search(domain)
            if search:
                categories = search_product.mapped('public_categ_ids')
                search_categories = Category.search(
                    [('id', 'parent_of', categories.ids)] + request.website.website_domain())
                categs = search_categories.filtered(lambda c: not c.parent_id)
            else:
                categs = Category.search([('parent_id', '=', False)] + request.website.website_domain())

            parent_category_ids = []
            if category:
                url = "/shop/category/%s" % slug(category)
                parent_category_ids = [category.id]
                current_category = category
                while current_category.parent_id:
                    parent_category_ids.append(current_category.parent_id.id)
                    current_category = current_category.parent_id

            product_count = len(search_product)
            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

            ProductAttribute = request.env['product.attribute']
            if products:
                # get all products without limit
                attributes = ProductAttribute.search([('attribute_line_ids.value_ids', '!=', False),
                                                      ('attribute_line_ids.product_tmpl_id', 'in', search_product.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)

            compute_currency = self._get_compute_currency(pricelist, products[:1])

            values = {
                'search': search,
                'category': category,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'pager': pager,
                'pricelist': pricelist,
                'add_qty': add_qty,
                'products': products,
                'search_count': product_count,  # common for all searchbox
                'bins': TableCompute().process(products, ppg),
                'rows': PPR,
                'categories': categs,
                'attributes': attributes,
                'compute_currency': compute_currency,
                'keep': keep,
                'parent_category_ids': parent_category_ids,
                'search_categories_ids': search_categories and search_categories.ids,
            }
            return request.render("website_adjustment.product_list", values)


class CustomerPortalManual(CustomerPortal):
    @http.route([
        '''/shop/product/download_manual/<int:product>''',
    ], type='http', auth="public", website=True)
    def download_manual(self, product, access_token=None):
        product_id = request.env['product.product'].browse(product)
        try:
            product_sudo = self._document_check_access('product.product', product_id, access_token=access_token)
        except (AccessError, MissingError):
            pass
        if product_id.manual_pdf:
            pdf = base64.b64decode(product_id.manual_pdf)
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            response = request.make_response(pdf, headers=pdfhttpheaders)
            response.headers.add('Content-Disposition', content_disposition(product_id.manual_pdf_name + '.pdf'))
            return response