from odoo import fields, models


class MahazAccountMove(models.Model):
    _inherit = "account.move"

    mahaz_task_id = fields.Many2one(
        "project.task", string="Task", ondelete="set null", index=True,
        check_company=True, copy=False,
    )
