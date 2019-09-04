# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class FollowupReportStatementCutoff(models.Model):
    _name = 'report.statement.cutoff'
    _auto = False
    _description = 'Statement Report (Month End+10)'
    _order = 'car_id'

    id = fields.Char(string='id')
    bforward = fields.Float(string='BF Amount')
    partner_number = fields.Char(string='Customer No.')
    name = fields.Char(string='Name')
    amount_total = fields.Float(string='Amount Total')
    outstanding = fields.Float(string='Outstanding')
    iyear = fields.Char(string='I year')
    imonth = fields.Char(string='I month')
    # partner_id = fields.Integer(string='partner_id')
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    start_date = fields.Date(string='Start Date')
    cutoff_date = fields.Date(string='Cutoff Date')
    bforward_date = fields.Date(string='Bforward date')
    statement_letter = fields.Char(string='Statement letter')
    statement_type = fields.Char(string='Statement type')
    statement_receive = fields.Char(string='Statement receive')
    car_number = fields.Char(string='Car number')
    car_id = fields.Integer(string='Car ID')
    # total = fields.Float(string='Total', compute="_compute_total")

    # @api.depends('bforward')
    # @api.depends('outstanding')
    # def _compute_total(self):
    #     for rec in self:
    #         rec.total = rec.bforward + rec.outstanding

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_statement_cutoff')
        self.env.cr.execute("""CREATE OR REPLACE VIEW public.report_statement_cutoff AS
 SELECT row_number() OVER () AS id,
    ( SELECT sum(x.bforward) AS bfrward
           FROM ( SELECT sum(bf.amount_total_signed) AS bforward
                   FROM account_invoice bf
                  WHERE bf.date_invoice IS NOT NULL AND bf.state::text <> 'cancel'::text AND bf.state::text <> 'xdraft'::text AND bf.date_invoice <= inv.bforward_date AND bf.partner_id = inv.partner_id
                UNION
                 SELECT sum(movl.balance_cash_basis) AS bforward
                   FROM account_payment pay
                     JOIN account_move mov ON pay.move_name::text = mov.name::text
                     JOIN account_move_line movl ON mov.id = movl.move_id
                  WHERE pay.state::text <> 'cancel'::text AND pay.state::text <> 'draft'::text AND pay.payment_date <= (inv.cutoff_date + ((10 || ' days'::text)::interval)) AND pay.partner_id = inv.partner_id AND movl.partner_id = inv.partner_id AND (movl.account_id = 8 OR movl.account_id = 211)) x) AS bforward,
    inv.partner_number,
    inv.name,
    inv.amount_total,
    inv.outstanding,
    inv.iyear,
    inv.imonth,
    inv.partner_id,
    inv.start_date,
    inv.cutoff_date,
    inv.bforward_date,
    inv.statement_letter,
    inv.statement_type,
    inv.company_id,
    inv.statement_receive,
    inv.car_number,
    inv.car_id
   FROM ( SELECT cust.partner_number,
            cust.name,
            sum(inv_1.amount_total) AS amount_total,
            sum(inv_1.residual) AS outstanding,
            date_part('year'::text, inv_1.quot_date)::character varying(255) AS iyear,
            date_part('month'::text, inv_1.quot_date)::character varying(255) AS imonth,
            inv_1.partner_id,
            concat(date_part('year'::text, inv_1.quot_date)::character varying(255), '-', date_part('month'::text, inv_1.quot_date)::character varying(255), '-1')::date AS start_date,
            (concat(date_part('year'::text, inv_1.quot_date)::character varying(255), '-', date_part('month'::text, inv_1.quot_date)::character varying(255), '-1')::date + ((1 || ' month'::text)::interval) - ((1 || ' days'::text)::interval))::date AS cutoff_date,
            (concat(date_part('year'::text, inv_1.quot_date)::character varying(255), '-', date_part('month'::text, inv_1.quot_date)::character varying(255), '-1')::date - ((1 || ' days'::text)::interval))::date AS bforward_date,
            cust.statement_letter,
            cust.statement_type,
            cust.statement_receive,
            inv_1.company_id,
            car.number AS car_number,
            car.id AS car_id
           FROM account_invoice inv_1
             JOIN res_partner cust ON inv_1.partner_id = cust.id
             JOIN account_payment_term payt ON inv_1.payment_term_id = payt.id
             JOIN car_number_option car ON cust.car_number = car.id
          WHERE inv_1.quot_date IS NOT NULL AND payt.name::text ~~ '%月結%'::text AND inv_1.state::text <> 'cancel'::text AND inv_1.state::text <> 'xdraft'::text
          GROUP BY inv_1.company_id, (date_part('year'::text, inv_1.quot_date)::character varying(255)), (date_part('month'::text, inv_1.quot_date)::character varying(255)), inv_1.partner_id, cust.partner_number, cust.name, cust.statement_letter, cust.statement_type, cust.statement_receive, car.number, car.id) inv
  WHERE inv.outstanding > 0::numeric
  ORDER BY inv.car_id""")
