from odoo import api, fields, models, _


class MahazProjectTask(models.Model):
    _inherit = "project.task"

    mahaz_purchase_request_ids = fields.One2many("purchase.request", "mahaz_task_id", copy=False)
    mahaz_purchase_request_count = fields.Integer(compute="_mahaz_compute_purchase_requests", compute_sudo=False)
    mahaz_can_read_purchase_request = fields.Boolean(compute="_mahaz_compute_purchase_request_access")
    mahaz_can_create_purchase_request = fields.Boolean(compute="_mahaz_compute_purchase_request_access")

    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_purchase_request_access(self):
        for task in self:
            task.mahaz_can_read_purchase_request = self.env["purchase.request"].has_access("read")
            task.mahaz_can_create_purchase_request = self.env["purchase.request"].has_access("create")

    @api.depends("mahaz_purchase_request_ids")
    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_purchase_requests(self):
        self._mahaz_count("purchase.request", "mahaz_purchase_request_count")

    def mahaz_action_view_purchase_requests(self):
        return self._mahaz_action("purchase.request", _("Purchase Requests"))

    def mahaz_action_create_purchase_request(self):
        return self._mahaz_action("purchase.request", _("Create Purchase Request"), create=True)
