# Copyright 2026 Mahaz (mahaz_abdullah@hotmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class AccountMove(models.Model):
    _inherit = "account.move"

    doodle_image = fields.Image(
        string="Invoice Doodle",
        max_width=1600,
        max_height=900,
        attachment=True,
        copy=False,
        help="Draw a doodle or upload an image to display on the invoice PDF.",
    )

    def _mahaz_check_doodle_write_access(self) -> None:
        # Keep invoice/portal read access intact; restrict mutations server-side.
        if not self.env.su and not self.env.user.has_group(
            "account.group_account_invoice"
        ):
            raise AccessError(
                _("Only users with invoicing access can change invoice doodles.")
            )

    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> models.Model:
        if any("doodle_image" in vals for vals in vals_list) or (
            "default_doodle_image" in self.env.context
        ):
            self._mahaz_check_doodle_write_access()
        return super().create(vals_list)

    def write(self, vals: dict) -> bool:
        if "doodle_image" in vals:
            self._mahaz_check_doodle_write_access()
        return super().write(vals)
