{
    "name": "Mahaz Project Task Integration",
    "version": "18.0.1.0.0",
    "category": "Services/Project",
    "summary": "Task expenses, purchases, invoices and Community documents",
    "author": "Mahaz",
    "license": "AGPL-3",
    "depends": ["project", "hr_expense", "purchase", "account", "mail"],
    "data": [
        "views/document_views.xml",
        "views/project_task_views.xml",
        "views/hr_expense_views.xml",
        "views/purchase_order_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
}
