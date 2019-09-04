from odoo import models, api
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            args = args or []
            domain = ['|', ('name', operator, name), ('partner_number', operator, name)]
            partners = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
            return self.browse(partners).name_get()
        return super(ResPartner, self)._name_search(name, args=args, operator=operator, limit=limit,
                                                    name_get_uid=name_get_uid)

    @api.multi
    def name_get(self):
        return [(partners.id, '%s%s' % (partners.partner_number and '[%s] ' % partners.partner_number or '', partners.name))
                for partners in self]
