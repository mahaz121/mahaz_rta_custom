Mahaz Invoice Doodles
====================

Maintainer: Mahaz <mahaz_abdullah@hotmail.com> | https://mahaz.uk

Version 18.0.1.3.0 provides a modern navy-and-sand invoice layout, bundled Cairo
Arabic/Latin fonts, decorative line art, and an optional saved drawing panel.
The standard invoice and optional GCC report use the layout. The companion
``mahaz_custom_invoice_doodles_gcc`` preserves the localization's invoice data,
Saudi QR payload, simplified invoice title, and issue timestamp.

The company header is part of the invoice body, so its height is not clipped
by wkhtmltopdf's separate header margin. It appears once per invoice. Standard
invoice downloads, PDF without Payment, and Fresh Print use the same dedicated
paper format. Other report actions and the company-wide paper format are not
modified. Long invoices repeat the line-table heading and PDF footer.

Logos and compact layout
------------------------

Raster logos are converted to RGB PNG for Qt, flattened on white, trimmed of
empty margins, and fitted without distortion onto a consistent canvas. The
original company logo is not modified. Unsupported formats (including SVG)
fall back to the original image and log a warning. For such a logo, an
administrator can upload a PNG under Settings > Companies > the company >
Mahaz Invoice Branding. This override applies only to that company's invoices.

Header/customer/date boxes are removed. Reduced padding and natural totals
pagination keep short invoices compact without shrinking fonts or hiding rows.
One-page output depends on descriptions, address length, notes, payments, and
drawings; large invoices continue onto additional pages. Local wkhtmltopdf
fixtures with one and eight ordinary lines fit one page; 40 lines use two.
These fixtures are not the user's Sana invoice or an Odoo database render.

Run the standalone logo tests with::

    python mahaz_custom_invoice_doodles/checks/test_logo.py

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
The static instances have distinct Mahaz Cairo family/style/PostScript names
so Qt does not collapse all weights into the same font during PDF generation.

Validation
----------

Before production rollout, print standard and Saudi invoices in staging,
including a credit note, discounts, long descriptions, multiple tax groups,
multiple pages, payment entries, and a saved drawing. Verify QR scanning and
company details. A local wkhtmltopdf 0.12.6 fixture verified the complete logo,
long company address, one-page body layout, and distinct embedded font weights.
It does not run the Odoo database or QWeb engine, so actual pagination and the
footer must also be checked in the deployment environment.

Security
--------

Doodle writes require the invoicing group, except in superuser mode. Invoice
ACLs and record rules remain in effect. ACL rows are additive and do not revoke
existing permissions. Report values use QWeb field/output directives. No
Enterprise dependency, raw SQL, or custom JavaScript is introduced.
