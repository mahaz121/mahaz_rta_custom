Mahaz Invoice Doodles
====================

Maintainer: Mahaz <mahaz_abdullah@hotmail.com> | https://mahaz.uk

Version 18.0.1.2.0 adds a modern navy-and-sand invoice layout, bundled Cairo
Arabic/Latin fonts, decorative line art, and an optional saved drawing panel.
The standard invoice and optional GCC report use the layout. The companion
``mahaz_custom_invoice_doodles_gcc`` preserves the localization's invoice data,
Saudi QR payload, simplified invoice title, and issue timestamp.

Deployment
----------

Copy both complete module directories, including ``static/``, to the addons
path. Restart Odoo and upgrade BOTH modules, not just the base module. Use
``Print > Mahaz Modern Invoice (Fresh Print)`` to render current data with the
dedicated A4 paper format. Existing issued PDF attachments are not rewritten.
This fresh print does not submit or reissue an electronic invoice.

The form's Invoice Notes & Doodles tab supports drawing, uploading, replacing,
and removing an image. Save before printing. Decorative line art appears even
without a saved image. The saved image remains optional and is not copied when
duplicating an invoice.

Fonts
-----

Cairo comes from https://github.com/google/fonts/tree/main/ofl/cairo.
The included static 400/600/700 TTF instances were generated from the upstream
variable font at slnt=0 for compatibility with older PDF renderers. They
contain Arabic and Latin glyphs. Its SIL Open Font License is distributed in
``static/src/fonts/OFL.txt``. Fonts are served locally by Odoo; there is no
Google Fonts request at print time. The report worker must be able to reach
Odoo's assets URL, as with all Odoo PDF report assets.

Validation
----------

Before production rollout, print standard and Saudi invoices in staging,
including a credit note, discounts, long descriptions, multiple tax groups,
multiple pages, payment entries, and a saved drawing. Verify QR scanning and
company details. The bundled browser design preview is not an Odoo/wkhtmltopdf
render; actual pagination must be checked in the deployment environment.

Security
--------

Doodle writes require the invoicing group, except in superuser mode. Invoice
ACLs and record rules remain in effect. ACL rows are additive and do not revoke
existing permissions. Report values use QWeb field/output directives. No
Enterprise dependency, raw SQL, or custom JavaScript is introduced.
