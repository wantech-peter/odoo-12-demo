from dateutil.relativedelta import relativedelta

from odoo import models, api, fields, _
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date


class ChangeDatePeriod(models.AbstractModel):
    _inherit = 'account.aged.partner'

    def _get_columns_name(self, options):
        '''splitted the column 1-30 t0 1-21 and 22-30'''

        columns = [{}]
        columns += [
            {'name': v, 'class': 'number', 'style': 'white-space:nowrap;'}
            for v in [_("JRNL"), _("Account"), _("Reference"),
                      _("Not due on: %s") % format_date(self.env,
                                                        options['date'][
                                                            'date']),
                      _("1 - 21"), _("22 - 30"), _("31 - 60"), _("61 - 90"),
                      _("91 - 120"), _("Older"), _("Total")]
        ]
        return columns

    @api.model
    def _get_lines(self, options, line_id=None):
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        results, total, amls = self.env[
            'report.account.report_agedpartnerbalance'].with_context(
            include_nullified_amount=True)._get_partner_move_lines(
            account_types, self._context['date_to'], 'posted', 30)

        for values in results:
            if line_id and 'partner_%s' % (values['partner_id'],) != line_id:
                continue
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 3 + [
                    {'name': self.format_value(sign * v)} for v in
                    [values['direction'], values['5'], values['4'],
                     values['3'], values['2'],
                     values['1'], values['0'], values['total']]],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'partner_%s' % (
                    values['partner_id'],) in options.get('unfolded_lines'),
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get(
                    'unfolded_lines'):
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    caret_type = 'account.move'
                    if aml.invoice_id:
                        caret_type = 'account.invoice.in' if aml.invoice_id.type in (
                            'in_refund',
                            'in_invoice') else 'account.invoice.out'
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    vals = {
                        'id': aml.id,
                        'name': format_date(self.env,
                                            aml.date_maturity or aml.date),
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in
                                    [aml.journal_id.code, aml.account_id.code,
                                     self._format_aml_name(aml)]] + \
                                   [{'name': v} for v in [line[
                                                              'period'] == 7 - i and self.format_value(
                                       sign * line['amount']) or '' for i in
                                                          range(8)]],
                        'action_context': aml.get_action_context(),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 3 + [
                    {'name': self.format_value(sign * v)} for v in
                    [total[7], total[5], total[4], total[3], total[2],
                     total[1], total[0], total[6]]],
            }
            lines.append(total_line)
        print("lines", lines)
        return lines

    class ReportAgedPartnerBalanceExtend(models.AbstractModel):

        _inherit = 'report.account.report_agedpartnerbalance'

        def _get_partner_move_lines(self, account_type, date_from, target_move,
                                    period_length):
            '''replaced _get_partner_move_lines function to split the date period '1-30' to 1-21 and 2-30
            in aged partner ledger'''
            ctx = self._context
            periods = {}
            date_from = fields.Date.from_string(date_from)
            start = date_from
            for i in range(6)[::-1]:
                stop = start - relativedelta(days=period_length)
                period_name = str(
                    (6 - (i + 1)) * period_length + 1) + '-' + str(
                    (6 - i) * period_length)
                period_stop = (start - relativedelta(days=1)).strftime(
                    '%Y-%m-%d')
                if i == 0:
                    period_name = '+' + str(4 * period_length)
                if i == 5:
                    stop = start - relativedelta(days=21)
                    period_name = '1-21'
                    period_stop = (start - relativedelta(days=1)).strftime(
                        '%Y-%m-%d')
                if i == 4:
                    stop = start - relativedelta(days=9)
                    period_name = '22-30'
                    period_stop = (start - relativedelta(days=1)).strftime(
                        '%Y-%m-%d')
                periods[str(i)] = {
                    'name': period_name,
                    'stop': period_stop,
                    'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop

            res = []
            total = []
            partner_clause = ''
            cr = self.env.cr
            user_company = self.env.user.company_id
            user_currency = user_company.currency_id
            company_ids = self._context.get('company_ids') or [user_company.id]
            move_state = ['draft', 'posted']
            if target_move == 'posted':
                move_state = ['posted']
            arg_list = (tuple(move_state), tuple(account_type))
            # build the reconciliation clause to see what partner needs to be printed
            reconciliation_clause = '(l.reconciled IS FALSE)'
            cr.execute(
                'SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where max_date > %s',
                (date_from,))
            reconciled_after_date = []
            for row in cr.fetchall():
                reconciled_after_date += [row[0], row[1]]
            if reconciled_after_date:
                reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
                arg_list += (tuple(reconciled_after_date),)
            if ctx.get('partner_ids'):
                partner_clause = 'AND (l.partner_id IN %s)'
                arg_list += (tuple(ctx['partner_ids'].ids),)
            if ctx.get('partner_categories'):
                partner_clause += 'AND (l.partner_id IN %s)'
                partner_ids = self.env['res.partner'].search(
                    [('category_id', 'in', ctx['partner_categories'].ids)]).ids
                arg_list += (tuple(partner_ids or [0]),)
            arg_list += (date_from, tuple(company_ids))
            query = '''
                        SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
                        FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
                        WHERE (l.account_id = account_account.id)
                            AND (l.move_id = am.id)
                            AND (am.state IN %s)
                            AND (account_account.internal_type IN %s)
                            AND ''' + reconciliation_clause + partner_clause + '''
                            AND (l.date <= %s)
                            AND l.company_id IN %s
                        ORDER BY UPPER(res_partner.name)'''
            cr.execute(query, arg_list)

            partners = cr.dictfetchall()
            # put a total of 0
            for i in range(8):
                total.append(0)

            # Build a string like (1,2,3) for easy use in SQL query
            partner_ids = [partner['partner_id'] for partner in partners if
                           partner['partner_id']]
            lines = dict(
                (partner['partner_id'] or False, []) for partner in partners)
            if not partner_ids:
                return [], [], {}

            # Use one query per period and store results in history (a list variable)
            # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
            history = []
            for i in range(6):
                args_list = (
                    tuple(move_state), tuple(account_type),
                    tuple(partner_ids),)
                dates_query = '(COALESCE(l.date_maturity,l.date)'

                if periods[str(i)]['start'] and periods[str(i)]['stop']:
                    dates_query += ' BETWEEN %s AND %s)'
                    args_list += (
                        periods[str(i)]['start'], periods[str(i)]['stop'])
                elif periods[str(i)]['start']:
                    dates_query += ' >= %s)'
                    args_list += (periods[str(i)]['start'],)
                else:
                    dates_query += ' <= %s)'
                    args_list += (periods[str(i)]['stop'],)
                args_list += (date_from, tuple(company_ids))

                query = '''SELECT l.id
                                FROM account_move_line AS l, account_account, account_move am
                                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                                    AND (am.state IN %s)
                                    AND (account_account.internal_type IN %s)
                                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                                    AND ''' + dates_query + '''
                                AND (l.date <= %s)
                                AND l.company_id IN %s
                                ORDER BY COALESCE(l.date_maturity, l.date)'''
                cr.execute(query, args_list)
                partners_amount = {}
                aml_ids = cr.fetchall()
                aml_ids = aml_ids and [x[0] for x in aml_ids] or []
                for line in self.env['account.move.line'].browse(
                        aml_ids).with_context(prefetch_fields=False):
                    partner_id = line.partner_id.id or False
                    if partner_id not in partners_amount:
                        partners_amount[partner_id] = 0.0
                    line_amount = line.company_id.currency_id._convert(
                        line.balance, user_currency, user_company, date_from)
                    if user_currency.is_zero(line_amount):
                        continue
                    for partial_line in line.matched_debit_ids:
                        if partial_line.max_date <= date_from:
                            line_amount += partial_line.company_id.currency_id._convert(
                                partial_line.amount, user_currency,
                                user_company,
                                date_from)
                    for partial_line in line.matched_credit_ids:
                        if partial_line.max_date <= date_from:
                            line_amount -= partial_line.company_id.currency_id._convert(
                                partial_line.amount, user_currency,
                                user_company,
                                date_from)

                    if not self.env.user.company_id.currency_id.is_zero(
                            line_amount):
                        partners_amount[partner_id] += line_amount
                        lines.setdefault(partner_id, [])
                        lines[partner_id].append({
                            'line': line,
                            'amount': line_amount,
                            'period': i + 1,
                        })
                history.append(partners_amount)

            # This dictionary will store the not due amount of all partners
            undue_amounts = {}
            query = '''SELECT l.id
                            FROM account_move_line AS l, account_account, account_move am
                            WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                                AND (am.state IN %s)
                                AND (account_account.internal_type IN %s)
                                AND (COALESCE(l.date_maturity,l.date) >= %s)\
                                AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                            AND (l.date <= %s)
                            AND l.company_id IN %s
                            ORDER BY COALESCE(l.date_maturity, l.date)'''
            cr.execute(query, (
                tuple(move_state), tuple(account_type), date_from,
                tuple(partner_ids),
                date_from, tuple(company_ids)))
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                partner_id = line.partner_id.id or False
                if partner_id not in undue_amounts:
                    undue_amounts[partner_id] = 0.0
                line_amount = line.company_id.currency_id._convert(
                    line.balance,
                    user_currency,
                    user_company,
                    date_from)
                if user_currency.is_zero(line_amount):
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount += partial_line.company_id.currency_id._convert(
                            partial_line.amount, user_currency, user_company,
                            date_from)
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount -= partial_line.company_id.currency_id._convert(
                            partial_line.amount, user_currency, user_company,
                            date_from)
                if not self.env.user.company_id.currency_id.is_zero(
                        line_amount):
                    undue_amounts[partner_id] += line_amount
                    lines.setdefault(partner_id, [])
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': 6,
                    })

            for partner in partners:
                if partner['partner_id'] is None:
                    partner['partner_id'] = False
                at_least_one_amount = False
                values = {}
                undue_amt = 0.0
                if partner[
                    'partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                    undue_amt = undue_amounts[partner['partner_id']]

                total[7] = total[7] + undue_amt
                values['direction'] = undue_amt
                if not float_is_zero(values['direction'],
                                     precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True

                for i in range(6):
                    during = False
                    if partner['partner_id'] in history[i]:
                        during = [history[i][partner['partner_id']]]
                    # Adding counter
                    total[(i)] = total[(i)] + (during and during[0] or 0)
                    values[str(i)] = during and during[0] or 0.0
                    if not float_is_zero(values[str(i)],
                                         precision_rounding=self.env.user.company_id.currency_id.rounding):
                        at_least_one_amount = True
                values['total'] = sum(
                    [values['direction']] + [values[str(i)] for i in range(6)])
                ## Add for total
                total[(i + 1)] += values['total']
                values['partner_id'] = partner['partner_id']
                if partner['partner_id']:
                    browsed_partner = self.env['res.partner'].browse(
                        partner['partner_id'])
                    values['name'] = browsed_partner.name and len(
                        browsed_partner.name) >= 45 and browsed_partner.name[
                                                        0:40] + '...' or browsed_partner.name
                    values['trust'] = browsed_partner.trust
                else:
                    values['name'] = _('Unknown Partner')
                    values['trust'] = False

                if at_least_one_amount or (
                        self._context.get('include_nullified_amount') and
                        lines[
                            partner['partner_id']]):
                    res.append(values)

            return res, total, lines
