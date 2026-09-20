from odoo import api, models


class MahazIrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _mahaz_document_tasks(self):
        return self.env["project.task"].browse([
            attachment.res_id for attachment in self
            if attachment.res_model == "project.task" and attachment.res_id
        ])

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._mahaz_document_tasks().invalidate_recordset(["mahaz_document_count"])
        return records

    def write(self, vals):
        tasks = self._mahaz_document_tasks()
        result = super().write(vals)
        (tasks | self._mahaz_document_tasks()).invalidate_recordset(["mahaz_document_count"])
        return result

    def unlink(self):
        tasks = self._mahaz_document_tasks()
        result = super().unlink()
        tasks.invalidate_recordset(["mahaz_document_count"])
        return result
