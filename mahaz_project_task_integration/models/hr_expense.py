from odoo import fields, models

from .mahaz_payment import mahaz_payment_sources


class MahazHrExpense(models.Model):
    _inherit = "hr.expense"

    mahaz_task_id = fields.Many2one(
        "project.task", string="Task", ondelete="set null", index=True,
        check_company=True, copy=False,
    )
    mahaz_payment_source = fields.Selection(
        mahaz_payment_sources, string="Payment Source", tracking=True,
        help="Workflow classification only. Paid By still controls standard expense accounting. "
             "Petty Cash does not create cash movements or select a journal.",
    )
