from collections import Counter

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class MahazProjectTask(models.Model):
    _inherit = "project.task"

    mahaz_expense_ids = fields.One2many("hr.expense", "mahaz_task_id", copy=False)
    mahaz_purchase_ids = fields.One2many("purchase.order", "mahaz_task_id", copy=False)
    mahaz_invoice_ids = fields.One2many("account.move", "mahaz_task_id", copy=False)
    mahaz_expense_count = fields.Integer(compute="_mahaz_compute_expenses", compute_sudo=False)
    mahaz_purchase_count = fields.Integer(compute="_mahaz_compute_purchases", compute_sudo=False)
    mahaz_invoice_count = fields.Integer(compute="_mahaz_compute_invoices", compute_sudo=False)
    mahaz_document_count = fields.Integer(compute="_mahaz_compute_documents", compute_sudo=False)
    mahaz_can_read_expense = fields.Boolean(compute="_mahaz_compute_access")
    mahaz_can_create_expense = fields.Boolean(compute="_mahaz_compute_access")
    mahaz_can_read_purchase = fields.Boolean(compute="_mahaz_compute_access")
    mahaz_can_create_purchase = fields.Boolean(compute="_mahaz_compute_access")
    mahaz_can_read_invoice = fields.Boolean(compute="_mahaz_compute_access")
    mahaz_can_create_invoice = fields.Boolean(compute="_mahaz_compute_access")
    mahaz_can_read_document = fields.Boolean(compute="_mahaz_compute_access")

    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_access(self):
        for key, model in (("expense", "hr.expense"), ("purchase", "purchase.order"),
                           ("invoice", "account.move"), ("document", "ir.attachment")):
            for task in self:
                task[f"mahaz_can_read_{key}"] = self.env[model].has_access("read")
                if key != "document":
                    task[f"mahaz_can_create_{key}"] = self.env[model].has_access("create")

    def _mahaz_count(self, model, field, extra_domain=None):
        """One grouped query per model/batch, in the caller's security context."""
        counts = {}
        records = self.env[model].with_context(active_test=False)
        ids = [task.id for task in self if task.id and isinstance(task.id, int)]
        if ids and records.has_access("read"):
            rows = records._read_group(
                [("mahaz_task_id", "in", ids)] + (extra_domain or []),
                ["mahaz_task_id"], ["__count"],
            )
            counts = {task.id: count for task, count in rows}
        for task in self:
            task[field] = counts.get(task.id, 0)

    @api.depends("mahaz_expense_ids")
    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_expenses(self):
        self._mahaz_count("hr.expense", "mahaz_expense_count")

    @api.depends("mahaz_purchase_ids")
    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_purchases(self):
        self._mahaz_count("purchase.order", "mahaz_purchase_count")

    def _mahaz_invoice_domain(self):
        return [("move_type", "in", ("out_invoice", "in_invoice", "out_refund", "in_refund"))]

    @api.depends("mahaz_invoice_ids", "mahaz_invoice_ids.move_type")
    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_invoices(self):
        self._mahaz_count("account.move", "mahaz_invoice_count", self._mahaz_invoice_domain())

    @api.depends_context("uid", "allowed_company_ids")
    def _mahaz_compute_documents(self):
        # search_read deliberately uses ir.attachment._search's parent-access filter.
        # Aggregating attachments directly can bypass that special security logic.
        ids = [task.id for task in self if task.id and isinstance(task.id, int)]
        rows = []
        if ids and self.env["ir.attachment"].has_access("read"):
            rows = self.env["ir.attachment"].search_read(
                [("res_model", "=", "project.task"), ("res_id", "in", ids),
                 ("res_field", "=", False)], ["res_id"],
            )
        counts = Counter(row["res_id"] for row in rows)
        for task in self:
            task.mahaz_document_count = counts.get(task.id, 0)

    def _mahaz_check_task(self):
        self.ensure_one()
        if not self.id or not isinstance(self.id, int):
            raise UserError(_("Save the task before opening related records."))
        self.check_access("read")
        if not self.exists():
            raise UserError(_("This task no longer exists."))

    def _mahaz_context(self):
        self._mahaz_check_task()
        # Do not inherit unrelated action defaults or search filters from the task.
        context = {key: value for key, value in self.env.context.items()
                   if not key.startswith(("default_", "search_default_"))
                   and not key.endswith("_view_ref")
                   and key not in ("active_id", "active_ids", "active_model", "group_by")}
        context.update(default_mahaz_task_id=self.id, active_test=False)
        if self.company_id:
            if self.company_id not in self.env.companies:
                raise AccessError(_("Select the task company before creating related records."))
            context["default_company_id"] = self.company_id.id
        return context

    def _mahaz_action(self, model, title, extra_domain=None, create=False, defaults=None):
        context = self._mahaz_context()
        records = self.env[model]
        records.check_access("create" if create else "read")
        context.update(defaults or {})
        domain = [("mahaz_task_id", "=", self.id)] + (extra_domain or [])
        action = {
            "type": "ir.actions.act_window", "name": title, "res_model": model,
            "view_mode": "form" if create else "list,form",
            "views": [(False, "form")] if create else [(False, "list"), (False, "form")],
            "domain": domain, "context": context, "target": "current",
        }
        return action

    def mahaz_action_view_expenses(self):
        return self._mahaz_action("hr.expense", _("Expenses"))

    def mahaz_action_create_expense(self):
        context = self._mahaz_context()
        company = self.company_id or self.env.company
        employee = self.env.user.with_company(company).employee_id
        if employee:
            context["default_employee_id"] = employee.id
        if self.project_id.account_id:
            context["default_analytic_distribution"] = {str(self.project_id.account_id.id): 100.0}
        return self._mahaz_action("hr.expense", _("Create Expense"), create=True, defaults=context)

    def mahaz_action_view_purchases(self):
        return self._mahaz_action("purchase.order", _("Purchases"))

    def mahaz_action_create_purchase(self):
        return self._mahaz_action("purchase.order", _("Create Purchase"), create=True)

    def mahaz_action_view_invoices(self):
        action = self._mahaz_action("account.move", _("Invoices"), self._mahaz_invoice_domain(),
                                    defaults={"default_move_type": "out_invoice"})
        action["views"] = [(self.env.ref("account.view_invoice_tree").id, "list"),
                           (self.env.ref("account.view_move_form").id, "form")]
        return action

    def mahaz_action_create_invoice(self):
        self._mahaz_check_task()
        defaults = {"default_move_type": "out_invoice"}
        if self.partner_id:
            defaults["default_partner_id"] = self.partner_id.id
        return self._mahaz_action("account.move", _("Create Invoice"), create=True, defaults=defaults)

    def mahaz_action_view_documents(self):
        context = self._mahaz_context()
        self.env["ir.attachment"].check_access("read")
        context.pop("default_mahaz_task_id", None)
        context.update(default_res_model="project.task", default_res_id=self.id,
                       default_type="binary", default_public=False)
        return {
            "type": "ir.actions.act_window", "name": _("Documents"),
            "res_model": "ir.attachment", "view_mode": "list,form",
            "views": [(self.env.ref("mahaz_project_task_integration.mahaz_document_list").id, "list"),
                      (self.env.ref("mahaz_project_task_integration.mahaz_document_form").id, "form")],
            "domain": [("res_model", "=", "project.task"), ("res_id", "=", self.id),
                       ("res_field", "=", False)],
            "context": context, "target": "current",
        }

    def unlink(self):
        # Standard ORM unlink destroys attachments. Preserve private originals,
        # including subtask attachments, only after checking deletion authority.
        tasks = self | self._get_all_subtasks()
        tasks.check_access("unlink")
        with self.env.cr.savepoint():
            # Narrow elevation is necessary to preserve other users' attachments
            # and binary-field attachments; never used for counts or actions.
            attachments = self.env["ir.attachment"].sudo().search([
                ("res_model", "=", "project.task"), ("res_id", "in", tasks.ids),
                "|", ("res_field", "=", False), ("res_field", "!=", False),
            ])
            attachments.write({"res_model": False, "res_id": 0, "res_field": False,
                               "public": False, "access_token": False})
            return super().unlink()
