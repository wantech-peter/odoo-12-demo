
from odoo import models, api, fields, _
from odoo.tools.misc import formatLang, format_date
import datetime
from odoo import tools


class AccountFollowupReportExtend(models.AbstractModel):
    _inherit = "account.followup.report"

    def _get_statement_report_lines(self, options, line_id=None):

        print("ffffffffffffffff",options)
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(
            options['partner_id']) or False
        start_date = options.get('start_date')
        cutoff_date = options.get('cutoff_date')
        if not partner:
            return []
        lang_code = partner.lang or self.env.user.lang or 'en_US'

        lines = []
        res = {}
        rec = {}
        today = fields.Date.today()
        line_num = 0
        for i in partner.invoice_ids:
            if i.state == 'draft':
                if i.company_id == self.env.user.company_id:
                    if self.env.context.get('print_mode'):
                        continue
                    currency = i.currency_id or i.company_id.currency_id
                    if currency not in res:
                        res[currency] = []
                    res[currency].append(i)
        for l in partner.unreconciled_aml_ids:
            if l.company_id == self.env.user.company_id:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            for aml in aml_recs:
                try:
                    amount = aml.currency_id and aml.amount_residual_currency or aml.amount_residual
                    date_due = format_date(self.env,
                                           aml.date_maturity or aml.date,
                                           lang_code=lang_code)
                    is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                    total += not aml.blocked and amount or 0
                    is_payment = aml.payment_id
                    if is_overdue or is_payment:
                        total_issued += not aml.blocked and amount or 0
                    move_line_name = aml.invoice_id.name or aml.name
                    expected_pay_date = format_date(self.env,
                                                    aml.expected_pay_date,
                                                    lang_code=lang_code) if aml.expected_pay_date else ''
                    invoice_ids = aml.invoice_id.origin
                    inv = aml.invoice_id.id
                    internal_note = aml.internal_note
                    is_blocked = aml.blocked
                    date_in_report = format_date(self.env,
                                                 aml.invoice_id.quot_date,
                                                 lang_code=lang_code)

                except AttributeError:
                    amount = aml.currency_id and aml.residual or aml.amount_total
                    date_due = aml.date_due
                    total += amount or 0
                    is_overdue = today > aml.date_due if aml.date_due else aml.quot_date
                    is_payment = self.env['account.payment']
                    if is_overdue or is_payment:
                        total_issued += amount or 0
                    move_line_name = aml.name
                    expected_pay_date = ''
                    invoice_ids = aml.origin
                    inv = aml.id
                    internal_note = ''
                    is_blocked = False
                    date_in_report = format_date(self.env, aml.quot_date,
                                                 lang_code=lang_code)
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date',
                                'style': 'white-space:nowrap;text-align:center;color: red;'}
                if is_payment:
                    date_due = ''

                if self.env.context.get('print_mode'):
                    move_line_name = {'name': move_line_name,
                                      'style': 'text-align:right; white-space:normal;'}
                amount = formatLang(self.env, amount, currency_obj=currency)
                line_num += 1
                columns = [
                    date_in_report,
                    date_due,
                    invoice_ids,
                    move_line_name,
                    expected_pay_date + ' ' + (internal_note or ''),
                    {'name': is_blocked, 'blocked': is_blocked},
                    amount,
                ]


                if self.env.context.get('print_mode'):
                    columns = columns[:4] + columns[6:]
                lines.append({
                    'id': aml.id,
                    'invoice_id': invoice_ids,
                    'view_invoice_id':
                        self.env['ir.model.data'].get_object_reference(
                            'account', 'invoice_form')[1],
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'invoice_id':inv,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'has_invoice': bool(invoice_ids),
                    'columns': [type(v) == dict and v or {'name': v} for v in
                                columns],
                })


            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'unfoldable': False,
                'level': 0,
                'columns': [{'name': v} for v in [''] * (
                    3 if self.env.context.get('print_mode') else 5) + [
                                total >= 0 and _('Total Due') or '',
                                total_due]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued,
                                          currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 0,
                    'columns': [{'name': v} for v in [''] * (
                        3 if self.env.context.get('print_mode') else 5) + [
                                    _('Total Overdue'), total_issued]],
                })
            # Add an empty line after the total to make a space between two currencies
            # line_num += 1
            # lines.append({
            #     'id': line_num,
            #     'name': '',
            #     'class': '',
            #     'unfoldable': False,
            #     'level': 0,
            #     'columns': [],
            # })

        count = 0
        for line in lines:
            if line.get('class') == 'total':
                count += 1
        lines = lines[:len(lines) - count]
        lines = sorted(lines, key=lambda x: x['columns'][0]['name'])
        is_year = False
        for line in lines:
            if line and line['columns']:
                sp = '/'
                stripped = line['columns'][0]['name'].split(sp, 1)[0]
                if stripped:
                    if len(stripped) == 4:
                        is_year = True
        if start_date and cutoff_date:

            if is_year:
                lines = list(filter(lambda x: datetime.datetime.strptime(x['columns'][0]['name'], '%Y/%m/%d') >=
                                              datetime.datetime.strptime(str(start_date), '%Y-%m-%d') and
                                              datetime.datetime.strptime(x['columns'][0]['name'], '%Y/%m/%d') <=
                                              datetime.datetime.strptime(str(cutoff_date), '%Y-%m-%d') if x['columns'][0]['name'] else None, lines))
            else:
                lines = list(filter(lambda x: datetime.datetime.strptime(x['columns'][0]['name'],'%m/%d/%Y') >=
                                              datetime.datetime.strptime(str(start_date),'%Y-%m-%d') and
                                              datetime.datetime.strptime(x['columns'][0]['name'],'%m/%d/%Y') <=
                                              datetime.datetime.strptime(str(cutoff_date),'%Y-%m-%d') if x['columns'][0]['name'] else None, lines))
        total = 0

        for line in lines:
            amount = line['columns'][6]['name'].replace('$', '')
            amount = amount.replace(',', '')
            total += float(amount)
            
        return {
            'followups': lines,
            'subtotal': total,
            'is_year': is_year,
        }