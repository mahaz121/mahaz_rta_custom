# Mahaz Project Task Integration — Odoo 18 Community

Odoo 18 Community addons for task expenses, purchases, invoices and documents, with optional OCA Purchase Request and Helpdesk integrations. No Enterprise dependencies.

## Modules

| Addon | Required dependencies | Features |
| --- | --- | --- |
| `mahaz_project_task_integration` | `project`, `hr_expense`, `purchase`, `account`, `mail` | Expenses, Documents, Purchases, Invoices; creation actions; payment classification; document retention |
| `mahaz_project_purchase_request` | Base addon and OCA `purchase_request` 18.0 | Purchase Requests smart button and creation, payment classification |
| `mahaz_project_helpdesk` | Base addon and OCA `helpdesk_mgmt` 18.0 | Tickets smart button, task field on `helpdesk.ticket` |

The four standard apps are **required** for the base addon and Odoo installs missing dependencies. The two OCA integrations are **optional**, installed explicitly, and absent from the base model registry and views. This follows the dependency list requested; no runtime model injection or Enterprise Helpdesk dependency is used. If standard Expenses or Purchase must also remain uninstalled, they would require additional separately packaged bridges.

With both bridges installed, the added smart buttons are ordered Expenses → Documents → Purchases → Purchase Requests → Tickets → Invoices. Existing Odoo smart buttons remain. Odoo may move buttons into its overflow menu on smaller screens.

## Behavior

- Counts include only records the current user can read, in enabled companies. Counts and actions include archived related records consistently. Business counts use one `_read_group` call per integration for a batch of tasks, without `sudo`. Document counts use a batched `search_read` so the special attachment parent-access filter runs. Counts are not stored; document hooks invalidate cached counts on upload, reassignment, and deletion.
- Buttons are hidden when model read/create ACLs are unavailable; opening an action checks both the task and target model. Existing record rules still govern the resulting list, form, creation and editing. Hiding a button is not the security boundary. Create permissions that depend on record values are enforced when saving.
- Actions always open list/form, including a single related record, so the task filter stays visible. Creation actions open an unsaved form in the current window. Canceling creates nothing. No order is confirmed and no invoice is posted.
- Expense creation prefills `mahaz_task_id`, the task company, the current user's employee in that company, and 100% of the project's existing `account_id` as `analytic_distribution`. Standard `hr.expense` has no project field; the task relation supplies project context without inventing one. No analytic account is created. Standard Odoo onchanges/distribution models may refine those defaults.
- Purchases link at order level, expenses at expense level, and invoices at move level. There is no automatic propagation between purchase orders, bills and expense reports. Link existing records through their Task Integration section.
- Invoice lists include customer invoices, vendor bills, customer refunds and vendor refunds. Journal entries and receipts are excluded. Create Invoice opens a draft **customer invoice**, with the task's customer when present. Vendor bills can be linked through their standard form.
- Payment Source is optional classification: `petty_cash`, `company`, `employee_reimbursement`. It deliberately does not synchronize or override standard Paid By (`payment_mode`), journals, payment processing or accounting entries. Select Paid By separately. A future addon can depend on this addon and consume `mahaz_payment_source` to integrate a real petty-cash ledger.
- The document action permits one file or URL per new attachment form and preserves `res_model='project.task'` and the current `res_id`. Existing chatter uploads also appear. Binary field storage attachments are excluded from the Documents list. Standard parent-record access is enforced by Odoo. No new attachment ACL is granted.
- Custom task relations are indexed, company checked, `copy=False` and `ondelete='set null'`. Duplicating a business record does not silently link its copy to the original task.

### Task deletion and retained documents

Odoo's base ORM deletes attachments attached to a deleted record. To satisfy the retention requirement, the task's `unlink` override first checks unlink access for all tasks that standard Odoo will delete, including the subtasks returned by Odoo. Inside a savepoint it detaches their attachments before calling the standard deletion chain. Failure rolls back the detachment.

This is the **only elevated operation**: a narrowly scoped `sudo()` search/write preserves all attachments, including those created by someone else and binary-field storage attachments. It cannot return hidden attachment data through actions or counts. Retained documents keep their original filename, data and creator; their model/record/field association is cleared, public access is disabled and access tokens are revoked. They remain accessible to their creator or a system administrator under standard unlinked-attachment rules. They no longer appear in a task's chatter or Documents button. Administrators can find them under Settings → Technical → Database Structure → Attachments (developer mode), or through the ORM, and reassign them after checking the destination's permissions. Keep a database/filestore backup for audit history; deleting a task still removes standard chatter history.

Uninstalling these addons does not delete the linked business records or attachments. Odoo drops the addon-owned fields and their classification/link values. Export those values before uninstalling if they must be retained. Once the base addon is uninstalled, Odoo's standard attachment deletion behavior resumes.

### Technical naming

All added fields, XML IDs, callable UI methods and module names use `mahaz_`. Private helpers use `_mahaz_`: the leading underscore prevents RPC access, as required for internal helpers that accept model/domain arguments. Standard framework overrides (`create`, `write`, `unlink`) and `__init__`/`__manifest__` keep their required names. There are no new business models, menus, groups, sequences or ACL CSV files.

## Installation

1. Back up the target database and filestore; first install on an Odoo **18.0 Community** staging database.
2. Copy the three `mahaz_*` directories into an existing custom addons directory, such as `/opt/odoo/custom-addons`.
3. Include that directory in `addons_path` alongside the standard addons paths in `odoo.conf`. Ensure the Odoo service account can read the files.
4. Restart Odoo, enable developer mode, select Apps → Update Apps List, clear the Apps-only search filter and install **Mahaz Project Task Integration**. Dependencies are installed automatically.
5. To enable Purchase Requests, use the OCA `purchase-workflow` **18.0** repository and install `purchase_request` and its declared dependencies. Then install **Mahaz Project Purchase Requests**.
6. To enable Tickets, use the OCA `helpdesk` **18.0** repository and install `helpdesk_mgmt` and its declared dependencies. Then install **Mahaz Project Tickets**. A different vendor's `helpdesk.ticket` implementation is not automatically compatible: adapt the isolated bridge manifest and inherited form XML ID after inspecting that vendor's model and views. Do not install Enterprise `helpdesk` to satisfy this bridge.

Example base installation, using a source checkout and existing configuration (replace paths/database/service names with your actual deployment):

```bash
sudo systemctl stop odoo18
sudo -u odoo /opt/odoo/venv/bin/python /opt/odoo/odoo-bin -c /etc/odoo18.conf -d mahaz_staging -i mahaz_project_task_integration --stop-after-init --no-http
sudo systemctl start odoo18
```

Optional installation once OCA addons are present in `addons_path`:

```bash
sudo -u odoo /opt/odoo/venv/bin/python /opt/odoo/odoo-bin -c /etc/odoo18.conf -d mahaz_staging -i mahaz_project_purchase_request,mahaz_project_helpdesk --stop-after-init --no-http
```

Stop other Odoo processes using that database before installation or upgrade. Check the command exits successfully before restarting workers. Configure normal Odoo company, employee, vendor/customer, accounting and access settings before using the actions.

## Upgrade and restart

Update only the modules installed in the target database:

```bash
sudo systemctl stop odoo18
sudo -u odoo /opt/odoo/venv/bin/python /opt/odoo/odoo-bin -c /etc/odoo18.conf -d mahaz_staging -u mahaz_project_task_integration,mahaz_project_purchase_request,mahaz_project_helpdesk --stop-after-init --no-http
sudo systemctl start odoo18
```

Base-only upgrade: use `-u mahaz_project_task_integration`.

Linux restart example: `sudo systemctl restart odoo18`.

Windows PowerShell examples (use your installed service name and paths):

```powershell
Stop-Service -Name 'odoo18'
& 'C:\Odoo18\python\python.exe' 'C:\Odoo18\server\odoo-bin' -c 'C:\Odoo18\server\odoo.conf' -d mahaz_staging -u mahaz_project_task_integration --stop-after-init --no-http
Start-Service -Name 'odoo18'
# For a restart without a module upgrade:
Restart-Service -Name 'odoo18'
```

## Troubleshooting

| Symptom | Check / correction |
| --- | --- |
| Addon does not appear | Verify its directory contains `__manifest__.py`, addons path, service restart, Apps List refresh and removal of the Apps-only filter. |
| Missing external ID | Confirm Odoo 18 Community and OCA 18.0; inspect the reported inherited view ID; ensure the upstream dependency is installed and upgraded. Do not substitute Enterprise view IDs. |
| Purchase Requests or Tickets absent | Install the corresponding OCA dependency **and** Mahaz bridge; updating the base alone cannot add these integrations. |
| Accounting/purchase button hidden | Grant the user's normal Odoo role only if appropriate. The addon intentionally does not grant accounting or purchasing access. |
| Count is lower than expected | Check task relation, record rules, enabled companies and move type. Counts represent records visible to that user. Refresh the task after edits from another session. |
| Create Expense cannot save | Configure an employee for the current user in the task company, an expense product, accounts and taxes. Review standard Paid By and analytic distribution. |
| Company mismatch on save | Enable/select the task company and ensure task, employee, document and journal belong to compatible companies. The addon does not bypass company restrictions. |
| Attachment upload denied | Check read/write permission on the task. Odoo's attachment model requires appropriate parent-record access even when the action can be opened. |
| Documents vanish from task after deletion | Expected: the task is gone. The creator/system administrator can recover retained private unlinked attachments; see retention policy above. |
| Payment Source does not pay/reimburse | Expected: this is classification only. Use standard expense accounting or a dedicated future petty-cash bridge. |
| View changes do not appear | Restart after Python changes and run the addon upgrade after XML/field changes. Inspect conflicting third-party inherited views. |

## License

AGPL-3. See [LICENSE](LICENSE).
