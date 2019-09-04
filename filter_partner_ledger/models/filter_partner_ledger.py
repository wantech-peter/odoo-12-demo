
from odoo import models, api, fields, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang, format_date, get_user_companies



class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_paymentterm = None

    @api.model
    def _get_options(self, previous_options=None):
        # Be sure that user has group analytic if a report tries to display analytic
        if self.filter_analytic:
            self.filter_analytic_accounts = [] if self.env.user.id in self.env.ref(
                'analytic.group_analytic_accounting').users.ids else None
            self.filter_analytic_tags = [] if self.env.user.id in self.env.ref(
                'analytic.group_analytic_tags').users.ids else None
            # don't display the analytic filtering options if no option would be shown
            if self.filter_analytic_accounts is None and self.filter_analytic_tags is None:
                self.filter_analytic = None
        if self.filter_partner:
            self.filter_partner_ids = []
            self.filter_partner_categories = []
            self.filter_paymentterm_ids = []
        return self._build_options(previous_options)

    def _set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        ctx = self.env.context.copy()
        if options.get('cash_basis'):
            ctx['cash_basis'] = True
        if options.get('date') and options['date'].get('date_from'):
            ctx['date_from'] = options['date']['date_from']
        if options.get('date'):
            ctx['date_to'] = options['date'].get('date_to') or options['date'].get('date')
        if options.get('all_entries') is not None:
            ctx['state'] = options.get('all_entries') and 'all' or 'posted'
        if options.get('journals'):
            ctx['journal_ids'] = [j.get('id') for j in options.get('journals') if j.get('selected')]
        company_ids = []
        if options.get('multi_company'):
            company_ids = [c.get('id') for c in options['multi_company'] if c.get('selected')]
            company_ids = company_ids if len(company_ids) > 0 else [c.get('id') for c in options['multi_company']]
        ctx['company_ids'] = len(company_ids) > 0 and company_ids or [self.env.user.company_id.id]
        if options.get('analytic_accounts'):
            ctx['analytic_account_ids'] = self.env['account.analytic.account'].browse([int(acc) for acc in options['analytic_accounts']])
        if options.get('analytic_tags'):
            ctx['analytic_tag_ids'] = self.env['account.analytic.tag'].browse([int(t) for t in options['analytic_tags']])
        if options.get('partner_ids'):
            ctx['partner_ids'] = self.env['res.partner'].browse([int(partner) for partner in options['partner_ids']])
        if options.get('partner_categories'):
            ctx['partner_categories'] = self.env['res.partner.category'].browse([int(category) for category in options['partner_categories']])
        if options.get('paymentterm_ids'):
            ctx['paymentterm_ids'] = self.env['account.payment.term'].browse([int(payterm) for payterm in options['paymentterm_ids']])
        print("ctx",ctx)
        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''

        print("optn", options)
        options = self._get_options(options)
        print("optn", options)
        # apply date and date_comparison filter
        self._apply_date_filter(options)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            searchview_dict['analytic_accounts'] = self.env.user.id in self.env.ref('analytic.group_analytic_accounting').users.ids and [(t.id, t.name) for t in self.env['account.analytic.account'].search([])] or False
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            searchview_dict['analytic_tags'] = self.env.user.id in self.env.ref('analytic.group_analytic_tags').users.ids and [(t.id, t.name) for t in self.env['account.analytic.tag'].search([])] or False
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in options['partner_categories']]
            options['selected_paymentterm_ids'] = [self.env['account.payment.term'].browse(int(pay_term)).name for pay_term in options['paymentterm_ids']]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))
        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view'].render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info


class AccountMoveLineInherit(models.AbstractModel):
     _inherit = "account.move.line"

     @api.model
     def _query_get(self, domain=None):
         self.check_access_rights('read')

         context = dict(self._context or {})
         print("gggggggggggggggggggggggg", context)
         domain = domain or []
         if not isinstance(domain, (list, tuple)):
             domain = safe_eval(domain)

         date_field = 'date'
         if context.get('aged_balance'):
             date_field = 'date_maturity'
         if context.get('date_to'):
             domain += [(date_field, '<=', context['date_to'])]
         if context.get('date_from'):
             if not context.get('strict_range'):
                 domain += ['|', (date_field, '>=', context['date_from']), (
                 'account_id.user_type_id.include_initial_balance', '=', True)]
             elif context.get('initial_bal'):
                 domain += [(date_field, '<', context['date_from'])]
             else:
                 domain += [(date_field, '>=', context['date_from'])]

         if context.get('journal_ids'):
             domain += [('journal_id', 'in', context['journal_ids'])]

         state = context.get('state')
         if state and state.lower() != 'all':
             domain += [('move_id.state', '=', state)]

         if context.get('company_id'):
             domain += [('company_id', '=', context['company_id'])]

         if 'company_ids' in context:
             domain += [('company_id', 'in', context['company_ids'])]

         if context.get('reconcile_date'):
             domain += ['|', ('reconciled', '=', False), '|', (
             'matched_debit_ids.max_date', '>', context['reconcile_date']), (
                        'matched_credit_ids.max_date', '>',
                        context['reconcile_date'])]

         if context.get('account_tag_ids'):
             domain += [
                 ('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]

         if context.get('account_ids'):
             domain += [('account_id', 'in', context['account_ids'].ids)]

         if context.get('analytic_tag_ids'):
             domain += [
                 ('analytic_tag_ids', 'in', context['analytic_tag_ids'].ids)]

         if context.get('analytic_account_ids'):
             domain += [('analytic_account_id', 'in',
                         context['analytic_account_ids'].ids)]

         if context.get('partner_ids'):
             domain += [('partner_id', 'in', context['partner_ids'].ids)]

         if context.get('partner_categories'):
             domain += [('partner_id.category_id', 'in',
                         context['partner_categories'].ids)]
         if context.get('paymentterm_ids'):
             partners = self.env['res.partner'].search([(
                                                        'property_payment_term_id',
                                                        'in', context[
                                                            'paymentterm_ids'].ids)])
             domain += [('partner_id', 'in', partners.ids)]
         where_clause = ""
         where_clause_params = []
         tables = ''
         if domain:
             query = self._where_calc(domain)

             # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
             self._apply_ir_rules(query)

             tables, where_clause, where_clause_params = query.get_sql()
         return tables, where_clause, where_clause_params


