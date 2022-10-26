# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import itemgetter
from markupsafe import Markup
from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.translate import _
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv.expression import OR
import base64

class CustomerPortal(portal.CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'repair_count' in counters:
            values['repair_count'] = (
                request.env['repair.order'].search_count([])
                if request.env['repair.order'].check_access_rights('read', raise_exception=False)
                else 0
            )
        return values

    def _ticket_get_page_view_values(self, repair, access_token, **kwargs):
        values = {
            'page_name': 'repair',
            'repair': repair,
        }
        return self._get_page_view_values(repair, access_token, values, 'my_repairs_history', False, **kwargs)

    @http.route(['/my/orders', '/my/order/page/<int:page>'], type='http', auth="user", website=True)
    def my_repair_orders(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='content', **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'state': {'label': _('Stage'), 'order': 'state'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'assigned': {'label': _('Assigned'), 'domain': [('user_id', '!=', False)]},
            'unassigned': {'label': _('Unassigned'), 'domain': [('user_id', '=', False)]},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>'))},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'name': {'input': 'name', 'label': _('Search in Reference')},
            'state': {'input': 'state', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'

        order = searchbar_sortings[sortby]['order']

        domain = searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search), ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain

        # pager
        tickets_count = request.env['repair.order'].search_count(domain)
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['repair.order'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_repairs_history'] = tickets.ids[:100]

        if groupby == 'stage':
            grouped_tickets = [request.env['repair.order'].concat(*g) for k, g in groupbyelem(tickets, itemgetter('state'))]
        else:
            grouped_tickets = [tickets]

        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'page_name': 'repair',
            'default_url': '/my/orders',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })
        return request.render("real_estate_maintenance.portal_repair_order", values)

    @http.route([
        "/repair/order/<int:ticket_id>",
        "/repair/order/<int:ticket_id>/<access_token>",
        '/my/order/<int:ticket_id>',
        '/my/order/<int:ticket_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def tickets_followup(self, ticket_id=None, access_token=None, **kw):
        try:
            ticket_sudo = self._document_check_access('repair.order', ticket_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._ticket_get_page_view_values(ticket_sudo, access_token, **kw)
        return request.render("real_estate_maintenance.repairs_followup", values)


class ServiceRequest(http.Controller):

    @http.route(['/repair_webform'], type='http', auth="public", website=True)
    def repair_webform(self):
        properties = request.env['product.product'].search([('product_tmpl_id.is_property','=',True)])
        buildings = request.env['building'].search([])
        values = {
            'properties': properties,
            'buildings': buildings
        }
        return request.render("real_estate_maintenance.create_repair", values)


    @http.route(['/create/webrepair'], type='http', auth="public", website=True)
    def create_repair(self, **kw):
        Attachments = request.env['ir.attachment']
        email = kw.get('email_id')
        if email:
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'email': email,
                    'name': kw.get('partner_name')
                })
        stock_warehouse = request.env['stock.warehouse'].search([('company_id', '=', request.env.company.id)], limit=1)
        repair_order= request.env['repair.order'].sudo().create({'partner_id': partner.id,
                                                   'product_id': kw.get('product_id'),
                                                   'building': kw.get('building'),
                                                   'product_uom': request.env.ref('uom.product_uom_unit').id,
                                                   'location_id': stock_warehouse.lot_stock_id.id,
                                                   'description': kw.get('description')})
        upload_file = kw['attachments']
        if upload_file:
            attachment_id = Attachments.sudo().create({
                'name': upload_file.filename,
                'type': 'binary',
                'datas': base64.encodestring(upload_file.read()),
                'public': True,
                'res_model': 'repair.order',
                'res_id': repair_order.id,
            })

            print(attachment_id,"S"*200)
        # {'partner_name': 'test', 'email_id': 'test@f.f', 'building': '1',
        # 'product_id': '65', 'description': 'test desc', 'attachments': ''}
        return request.render("real_estate_maintenance.repair_thanks", {})