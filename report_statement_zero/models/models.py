# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ReportStatementZero(models.Model):
    _name = 'report.statement.zero'
    _auto = False
    _description = 'report statement zero'
    #_order = 'productcode asc, custname asc'

    id = fields.Char(string='id')
    bforward = fields.Float(string='bforward')
    partner_number = fields.Char(string='partner_number')
    name = fields.Char(string='name')
    amount_total = fields.Integer(string='amount_total')
    outstanding = fields.Integer(string='outstanding')
    partner_id = fields.Integer(string='partner_id')
    start_date = fields.Date(string='start_date')
    cutoff_date = fields.Date(string='cutoff_date')
    bforward_date = fields.Date(string='bforward_date')
    statement_letter = fields.Boolean(string='statement_letter')
    statement_type = fields.Char(string='statement_type')
    statement_receive = fields.Char(string='statement_receive')
    company_id = fields.Integer(string='company_id')
    car_number = fields.Char(string='car_number')
    car_id = fields.Integer(string='car_id')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_statement_zero')
        self.env.cr.execute("""CREATE OR REPLACE VIEW public.report_statement_zero AS
 SELECT row_number() OVER () AS id,
    y.bforward,
    cust.partner_number,
    cust.name,
    0 AS amount_total,
    0 AS outstanding,
    cust.id AS partner_id,
    concat(date_part('year'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-', date_part('month'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-1')::date AS start_date,
    (concat(date_part('year'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-', date_part('month'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-1')::date + ((1 || ' month'::text)::interval) - ((1 || ' days'::text)::interval))::date AS cutoff_date,
    (concat(date_part('year'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-', date_part('month'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-1')::date - ((1 || ' days'::text)::interval))::date AS bforward_date,
    cust.statement_letter,
    cust.statement_type,
    cust.statement_receive,
    cust.company_id,
    car.number AS car_number,
    car.id AS car_id
   FROM ( SELECT x.partner_id,
            x.bforward
           FROM ( SELECT bforward.partner_id,
                    sum(bforward.bforward) AS bforward
                   FROM ( SELECT bf.partner_id,
                            sum(bf.amount_total_signed) AS bforward
                           FROM account_invoice bf
                          WHERE bf.date_invoice IS NOT NULL AND bf.state::text <> 'cancel'::text AND bf.state::text <> 'xdraft'::text AND bf.date_invoice <= (concat(date_part('year'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-', date_part('month'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-1')::date - ((1 || ' days'::text)::interval))::date
                          GROUP BY bf.partner_id
                        UNION
                         SELECT pay.partner_id,
                            sum(movl.balance_cash_basis) AS bforward
                           FROM account_payment pay
                             JOIN account_move mov ON pay.move_name::text = mov.name::text
                             JOIN account_move_line movl ON mov.id = movl.move_id
                          WHERE pay.state::text <> 'cancel'::text AND pay.state::text <> 'draft'::text AND pay.payment_date <= (concat(date_part('year'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-', date_part('month'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date)::character varying(255), '-1')::date - ((1 || ' days'::text)::interval))::date AND pay.partner_id = movl.partner_id AND (movl.account_id = 8 OR movl.account_id = 211)
                          GROUP BY pay.partner_id) bforward
                  GROUP BY bforward.partner_id) x
          WHERE NOT (EXISTS ( SELECT inv.id,
                    inv.access_token,
                    inv.message_main_attachment_id,
                    inv.name,
                    inv.origin,
                    inv.type,
                    inv.refund_invoice_id,
                    inv.number,
                    inv.move_name,
                    inv.reference,
                    inv.comment,
                    inv.state,
                    inv.sent,
                    inv.date_invoice,
                    inv.date_due,
                    inv.partner_id,
                    inv.vendor_bill_id,
                    inv.payment_term_id,
                    inv.date,
                    inv.account_id,
                    inv.move_id,
                    inv.amount_untaxed,
                    inv.amount_untaxed_signed,
                    inv.amount_tax,
                    inv.amount_total,
                    inv.amount_total_signed,
                    inv.amount_total_company_signed,
                    inv.currency_id,
                    inv.journal_id,
                    inv.company_id,
                    inv.reconciled,
                    inv.partner_bank_id,
                    inv.residual,
                    inv.residual_signed,
                    inv.residual_company_signed,
                    inv.user_id,
                    inv.fiscal_position_id,
                    inv.commercial_partner_id,
                    inv.cash_rounding_id,
                    inv.incoterm_id,
                    inv.source_email,
                    inv.vendor_display_name,
                    inv.create_uid,
                    inv.create_date,
                    inv.write_uid,
                    inv.write_date,
                    inv.team_id,
                    inv.partner_shipping_id,
                    inv.purchase_id,
                    inv.vendor_bill_purchase_id,
                    inv.incoterms_id,
                    inv.website_id,
                    inv.campaign_id,
                    inv.source_id,
                    inv.medium_id,
                    inv.custom_seq,
                    inv.system_seq,
                    inv.number_car,
                    inv.x_studio_car_number,
                    inv.x_studio_invoice_date,
                    inv.sale_order,
                    inv.payment_date,
                    inv.quot_date,
                    inv.invoice_partner,
                    inv.payment_method_id
                   FROM account_invoice inv
                  WHERE date_part('month'::text, inv.quot_date) = date_part('month'::text, (CURRENT_DATE - ((1 || ' month'::text)::interval))::date) AND inv.partner_id = x.partner_id)) AND x.bforward > 0::numeric) y
     JOIN res_partner cust ON y.partner_id = cust.id
     JOIN car_number_option car ON cust.car_number = car.id
        """)