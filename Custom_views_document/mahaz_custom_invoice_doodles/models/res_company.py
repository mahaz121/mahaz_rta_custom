# Copyright 2026 Mahaz (mahaz_abdullah@hotmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

import binascii
import logging

from PIL import Image

from odoo import api, fields, models

from ..logo_utils import prepare_invoice_logo

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    mahaz_invoice_logo = fields.Image(
        string="Mahaz Invoice Logo",
        max_width=1200,
        max_height=600,
        help="Optional invoice-only logo. Upload a PNG for PDF compatibility. "
        "Leave empty to use the company logo.",
    )
    mahaz_invoice_logo_print = fields.Binary(
        string="Mahaz Print Logo",
        compute="_compute_mahaz_invoice_logo_print",
        compute_sudo=False,
    )

    @api.depends("logo", "mahaz_invoice_logo")
    def _compute_mahaz_invoice_logo_print(self) -> None:
        for company in self:
            source_company = company.with_context(bin_size=False)
            source = source_company.mahaz_invoice_logo or source_company.logo
            if not source:
                company.mahaz_invoice_logo_print = False
                continue
            try:
                company.mahaz_invoice_logo_print = prepare_invoice_logo(source)
            except (ValueError, OSError, binascii.Error, Image.DecompressionBombError):
                # SVG or another unsupported image retains its original rendering.
                # The optional PNG override provides an administrative fallback.
                _logger.warning(
                    "Mahaz invoice logo normalization failed for company %s; "
                    "using the original image. Upload a PNG invoice logo if needed.",
                    company.id,
                )
                company.mahaz_invoice_logo_print = source
