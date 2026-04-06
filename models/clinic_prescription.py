from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class ClinicPrescription(models.Model):
    _name = "clinic.prescription"
    _description = "Clinic Prescription"
    _order = "prescription_date desc"

    # ── Fields ─────────────────────────────────────────────────────────────────
    name = fields.Char(default="New", copy=False)

    patient_id = fields.Many2one("clinic.patient", required=True)

    appointment_id = fields.Many2one(
        "clinic.appointment",
        domain="[('patient_id', '=', patient_id)]",
    )

    doctor_name = fields.Char(required=True)

    prescription_date = fields.Date(default=fields.Date.today, required=True)

    notes = fields.Text()

    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued"), ("completed", "Completed")],
        default="draft",
    )

    line_ids = fields.One2many(
        "clinic.prescription.line", "prescription_id", string="Medicines"
    )

    # ── Smart Feature: Allergy Conflict Detection ─────────────────────────────
    # Mirrors _compute_best_price pattern — reads across related records
    has_allergy_conflict = fields.Boolean(
        compute="_compute_allergy_conflict",
        store=True,
    )

    conflict_medicine_names = fields.Char(
        compute="_compute_allergy_conflict",
        store=True,
    )

    @api.depends("line_ids.medicine_id", "patient_id.allergy_ids")
    def _compute_allergy_conflict(self):
        for record in self:
            patient_allergies = record.patient_id.allergy_ids.mapped("name")
            conflicts = []
            for line in record.line_ids:
                if line.medicine_id and line.medicine_id.name in patient_allergies:
                    conflicts.append(line.medicine_id.name)
            record.has_allergy_conflict = bool(conflicts)
            record.conflict_medicine_names = ", ".join(conflicts) if conflicts else ""

    # ── Sequence on Create ─────────────────────────────────────────────────────
    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("clinic.prescription") or "New"
            )
        return super().create(vals)

    # ── Business Logic (mirrors sell_property guard pattern) ──────────────────
    def action_issue(self):
        for record in self:
            if record.state != "draft":
                raise UserError("Only draft prescriptions can be issued.")
            if record.has_allergy_conflict:
                raise ValidationError(
                    "Allergy conflict detected for: %s\n"
                    "Please remove or replace the medicine before issuing."
                    % record.conflict_medicine_names
                )
            if not record.line_ids:
                raise ValidationError("Cannot issue a prescription with no medicines.")
            record.state = "issued"

    def action_complete(self):
        for record in self:
            if record.state != "issued":
                raise UserError("Only issued prescriptions can be marked completed.")
            record.state = "completed"

    def action_reset_draft(self):
        for record in self:
            if record.state == "completed":
                raise UserError("A completed prescription cannot be reset.")
            record.state = "draft"


class ClinicPrescriptionLine(models.Model):
    _name = "clinic.prescription.line"
    _description = "Prescription Line"

    prescription_id = fields.Many2one(
        "clinic.prescription", required=True, ondelete="cascade"
    )
    medicine_id = fields.Many2one("clinic.medicine", required=True)
    dosage = fields.Char(required=True)
    frequency = fields.Selection(
        [
            ("once", "Once daily"),
            ("twice", "Twice daily"),
            ("three", "Three times daily"),
            ("asneeded", "As needed"),
        ],
        required=True,
    )
    duration_days = fields.Integer()
    notes = fields.Char()
