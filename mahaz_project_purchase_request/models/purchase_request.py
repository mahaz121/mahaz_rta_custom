from odoo import fields, models

from odoo.addons.mahaz_project_task_integration.models.mahaz_payment import mahaz_payment_sources


class MahazRelatedRecord(models.Model):
    _inherit = "purchase.request"
    _check_company_auto = True

    mahaz_task_id = fields.Many2one(
        "project.task", string="Task", ondelete="set null", index=True,
        check_company=True, copy=False,
    )

    mahaz_payment_source = fields.Selection(
        mahaz_payment_sources, string="Payment Source", tracking=True,
        help="Classification only; this does not create accounting or petty-cash entries.",
    )
