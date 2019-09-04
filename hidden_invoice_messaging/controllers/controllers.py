import base64
import logging
import psycopg2
import werkzeug
import json
from datetime import datetime
from math import ceil
from werkzeug import url_encode
from odoo import api, fields, http, registry, SUPERUSER_ID, _
from odoo.addons.web.controllers.main import binary_content , Session
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq, pycompat, ustr
from itertools import groupby


_logger = logging.getLogger(__name__)


class HiddenInvoiceMessaging(Session):

    @http.route('/mail/init_messaging', type='json', auth='user')
    def mail_init_messaging(self):
        values = {
            'needaction_inbox_counter': request.env['res.partner'].get_needaction_count(),
            'starred_counter': request.env['res.partner'].get_starred_count(),
            'channel_slots': request.env['mail.channel'].channel_fetch_slot(),
            'wantech':"wantech",
            # 'mail_failures': request.env['mail.message'].message_fetch_failed(),
            'commands': request.env['mail.channel'].get_mention_commands(),
            'mention_partner_suggestions': request.env['res.partner'].get_static_mention_suggestions(),
            'shortcodes': request.env['mail.shortcode'].sudo().search_read([], ['source', 'substitution', 'description']),
            'menu_id': request.env['ir.model.data'].xmlid_to_res_id('mail.menu_root_discuss'),
            'is_moderator': request.env.user.is_moderator,
            'moderation_counter': request.env.user.moderation_counter,
            'moderation_channel_ids': request.env.user.moderation_channel_ids.ids,
        }
        return values
