
from odoo import models, api, fields, _


class ResPartnerAudit(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_auditlog_report(self):
        ids = self.search([], limit=1).ids
        action = self.env.ref('auditlog_report.action_auditlog_report').report_action(ids)
        return action
