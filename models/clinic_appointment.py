from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class ClinicAppointment(models.Model):
    _name = "clinic.appointment"
    _description = "Clinic Appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "appointment_date desc"

    # ── Fields ─────────────────────────────────────────────────────────────────
    name = fields.Char(default="New", copy=False)

    patient_id = fields.Many2one("clinic.patient", required=True, tracking=True)

    doctor_name = fields.Char(required=True, tracking=True)

    appointment_date = fields.Date(required=True, tracking=True)

    appointment_time = fields.Float()

    appointment_type = fields.Selection(
        [
            ("checkup", "General Checkup"),
            ("followup", "Follow-Up"),
            ("emergency", "Emergency"),
            ("specialist", "Specialist"),
        ],
        default="checkup",
        required=True,
    )

    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("missed", "Missed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
        tracking=True,
    )

    notes = fields.Text()

    # ── Smart Feature: No-Show Probability ────────────────────────────────────
    no_show_probability = fields.Integer(
        compute="_compute_no_show_probability",
        store=True,
    )

    @api.depends("patient_id.missed_appointments", "appointment_type")
    def _compute_no_show_probability(self):
        for record in self:
            prob = 10
            if record.patient_id:
                prob += record.patient_id.missed_appointments * 15
            if record.appointment_type == "emergency":
                prob = max(prob - 20, 5)
            if record.appointment_type == "checkup":
                prob += 5
            record.no_show_probability = min(prob, 95)

    # ── Sequence on Create ─────────────────────────────────────────────────────
    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("clinic.appointment") or "New"
                )
        return super().create(vals_list)

    # ── SQL Constraints ────────────────────────────────────────────────────────
    _sql_constraints = [
        (
            "check_appointment_time",
            "CHECK(appointment_time >= 0 AND appointment_time < 24)",
            "Appointment time must be between 0 and 24.",
        ),
    ]

    # ── Python Constraints ─────────────────────────────────────────────────────
    @api.constrains("appointment_date")
    def _check_appointment_date(self):
        for record in self:
            if record.state == "scheduled" and record.appointment_date < fields.Date.today():
                raise ValidationError("Cannot schedule a new appointment in the past.")

    # ── Business Logic ─────────────────────────────────────────────────────────
    def action_confirm(self):
        for record in self:
            if record.state != "scheduled":
                raise UserError("Only scheduled appointments can be confirmed.")
            record.state = "confirmed"

    def action_done(self):
        for record in self:
            if record.state not in ("scheduled", "confirmed"):
                raise UserError("Only scheduled or confirmed appointments can be marked done.")
            record.state = "done"

    def action_missed(self):
        for record in self:
            record.state = "missed"

    def action_cancel(self):
        for record in self:
            if record.state == "done":
                raise UserError("A completed appointment cannot be cancelled.")
            record.state = "cancelled"

    # ── Cron Method ────────────────────────────────────────────────────────────
    @api.model
    def action_cron_mark_missed(self):
        """
        Runs every night via ir.cron.
        Finds all appointments that are still 'scheduled' or 'confirmed'
        but whose date has already passed — marks them 'missed' automatically.
        This triggers recompute of patient risk scores via the depends chain.
        """
        today = fields.Date.today()
        overdue = self.search([
            ("appointment_date", "<", today),
            ("state", "in", ("scheduled", "confirmed")),
        ])
        for appt in overdue:
            appt.state = "missed"