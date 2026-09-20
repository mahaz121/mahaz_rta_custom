from odoo import fields, models


class MahazRelatedRecord(models.Model):
    _inherit = "helpdesk.ticket"
    _check_company_auto = True

    mahaz_task_id = fields.Many2one(
        "project.task", string="Task", ondelete="set null", index=True,
        check_company=True, copy=False,
    )
