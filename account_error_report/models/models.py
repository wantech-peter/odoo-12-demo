# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportAccountError(models.Model):
    _name = 'account.error.report'
    _auto = False
    _description = 'account error report'
    #_order = 'productcode asc, custname asc'

    id = fields.Char(string='id')
    partner_id = fields.Integer(string='partner_id')
    name = fields.Char(string='Customer Name')
    account_balance = fields.Float(string='Ledger Balance')
    inv_balance = fields.Float(string='Invoice Balance')
    statement_balance = fields.Float(string='Statement Balance')
    diffa = fields.Integer(string='Diff A')
    diffb = fields.Integer(string='Diff B')
    month = fields.Integer(string='Month')
    partner_number = fields.Char(string='Customer No.')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'account_error_report')
        self.env.cr.execute("""CREATE OR REPLACE VIEW public.account_error_report AS
 SELECT row_number() OVER () AS id,
    x.partner_id,
    x.name,
    x.account_balance,
    x.inv_balance,
    x.statement_balance,
    x.diffa,
    x.diffb,
    x.month,
    x.partner_number
   FROM ( SELECT DISTINCT invb.partner_id,
            cust.name,
            accb.balance AS account_balance,
            invb.balance AS inv_balance,
            invb.balance AS statement_balance,
            accb.balance - invb.balance AS diffa,
            accb.balance - invb.balance AS diffb,
            0::double precision AS month,
            cust.partner_number
           FROM ( SELECT inv.partner_id,
                    sum(inv.balance) AS balance
                   FROM ( SELECT inv_1.partner_id,
                            sum(inv_1.amount_total_signed) AS balance
                           FROM account_invoice inv_1
                          WHERE inv_1.state::text <> 'xdraft'::text AND inv_1.state::text <> 'draft'::text AND inv_1.state::text <> 'cancel'::text
                          GROUP BY inv_1.partner_id
                        UNION
                         SELECT pay.partner_id,
                            sum(movel.balance::integer::numeric) AS balance
                           FROM account_payment pay
                             JOIN account_move mov ON pay.move_name::text = mov.name::text
                             JOIN account_move_line movel ON mov.id = movel.move_id
                          WHERE pay.state::text <> 'draft'::text AND pay.state::text <> 'cancelled'::text AND movel.account_id = 8 AND mov.state::text = 'posted'::text
                          GROUP BY pay.partner_id) inv
                  GROUP BY inv.partner_id) invb
             JOIN ( SELECT movel.partner_id,
                    sum(movel.balance) AS balance
                   FROM account_move_line movel
                     JOIN account_move mov ON movel.move_id = mov.id
                  WHERE movel.account_id = 8 AND mov.state::text = 'posted'::text
                  GROUP BY movel.partner_id) accb ON invb.partner_id = accb.partner_id
             JOIN res_partner cust ON invb.partner_id = cust.id
             JOIN ( SELECT replace(ir_property.res_id::text, 'res.partner,'::text, ''::text)::integer AS partner_id
                   FROM ir_property
                  WHERE ir_property.name::text = 'property_payment_term_id'::text AND (ir_property.value_reference::text = 'account.payment.term,3'::text OR ir_property.value_reference::text = 'account.payment.term,12'::text)) pterms ON cust.id = pterms.partner_id) x
        """)