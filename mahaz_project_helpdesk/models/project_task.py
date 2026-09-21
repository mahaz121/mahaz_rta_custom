from odoo import api, fields, models, _


class MahazProjectTask(models.Model):
    _inherit = "project.task"

    mahaz_ticket_ids = fields.One2many("helpdesk.ticket", "mahaz_task_id", copy=False)
    mahaz_ticket_count = fields.Integer(compute="_mahaz_compute_tickets", compute_sudo=False)
    mahaz_can_read_ticket = fields.Boolean(compute="_mahaz_compute_ticket_access")
    mahaz_can_create_ticket = fields.Boolean(compute="_mahaz_compute_ticket_access")

    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_ticket_access(self):
        for task in self:
            task.mahaz_can_read_ticket = self.env["helpdesk.ticket"].has_access("read")
            task.mahaz_can_create_ticket = self.env["helpdesk.ticket"].has_access("create")

    @api.depends("mahaz_ticket_ids")
    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_tickets(self):
        self._mahaz_count("helpdesk.ticket", "mahaz_ticket_count")

    def mahaz_action_view_tickets(self):
        return self._mahaz_action("helpdesk.ticket", _("Tickets"))

    def mahaz_action_create_ticket(self):
        return self._mahaz_action("helpdesk.ticket", _("Create Ticket"), create=True)
