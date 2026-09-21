# Copyright 2026 Mahaz (mahaz_abdullah@hotmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Mahaz Invoice Doodles",
    "summary": "Draw or upload doodles on customer invoices and credit notes",
    "version": "18.0.1.2.1",
    "category": "Accounting/Accounting",
    "author": "Mahaz",
    "website": "https://mahaz.uk",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/report_invoice_templates.xml",
        "views/report_modern_layout.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "mahaz_custom_invoice_doodles/static/src/css/invoice.css",
        ],
    },
    "installable": True,
    "application": False,
}
