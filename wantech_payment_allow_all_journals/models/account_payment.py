from odoo import models, fields,api, _


class AccountAbstractPaymentInherit(models.AbstractModel):
    """Rewriting the 'journal_id' field to avoid the default domain in bank and cash."""
    _inherit = "account.abstract.payment"

    @api.onchange('journal_id')
    def _onchange_journal(self):

        res = super(AccountAbstractPaymentInherit, self)._onchange_journal()
        if res.get('domain'):
            res['domain'].update({
                'journal_id': [('active', '=', True)],  # Passing all journals to selection
            })
        return res

