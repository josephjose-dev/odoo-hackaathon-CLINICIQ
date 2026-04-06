from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class ClinicPatient(models.Model):
    _name = "clinic.patient"
    _description = "Clinic Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "risk_score desc"

    # ── Basic Info ─────────────────────────────────────────────────────────────
    name = fields.Char(required=True, tracking=True)
    age = fields.Integer(tracking=True)
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")]
    )
    phone = fields.Char()
    email = fields.Char()
    date_of_birth = fields.Date()
    blood_type = fields.Selection(
        [
            ("a+", "A+"), ("a-", "A-"),
            ("b+", "B+"), ("b-", "B-"),
            ("ab+", "AB+"), ("ab-", "AB-"),
            ("o+", "O+"), ("o-", "O-"),
        ]
    )
    notes = fields.Text()

    # ── Status ─────────────────────────────────────────────────────────────────
    state = fields.Selection(
        [
            ("active", "Active"),
            ("critical", "Critical"),
            ("recovered", "Recovered"),
            ("inactive", "Inactive"),
        ],
        default="active",
        tracking=True,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    chronic_condition_ids = fields.Many2many("clinic.condition", tracking=True)
    allergy_ids = fields.Many2many("clinic.allergy")
    appointment_ids = fields.One2many("clinic.appointment", "patient_id")
    prescription_ids = fields.One2many("clinic.prescription", "patient_id")

    # ── Computed Fields ────────────────────────────────────────────────────────
    appointment_count = fields.Integer(compute="_compute_appointment_count")

    missed_appointments = fields.Integer(
        compute="_compute_missed_appointments",
        store=True,
    )

    last_visit_days = fields.Integer(
        compute="_compute_last_visit_days",
        store=True,
    )

    risk_score = fields.Integer(
        compute="_compute_risk_score",
        store=True,
    )

    risk_level = fields.Selection(
        [
            ("low", "Low"),
            ("moderate", "Moderate"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        compute="_compute_risk_score",
        store=True,
    )

    overdue_checkup = fields.Boolean(
        compute="_compute_overdue_checkup",
        store=True,
        string="Overdue for Checkup",
    )

    # ── Compute Methods ────────────────────────────────────────────────────────
    @api.depends("appointment_ids")
    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = len(record.appointment_ids)

    @api.depends("appointment_ids.state")
    def _compute_missed_appointments(self):
        for record in self:
            record.missed_appointments = len(
                record.appointment_ids.filtered(lambda a: a.state == "missed")
            )

    @api.depends("appointment_ids.appointment_date", "appointment_ids.state")
    def _compute_last_visit_days(self):
        today = fields.Date.today()
        for record in self:
            done = record.appointment_ids.filtered(
                lambda a: a.state == "done"
            ).sorted("appointment_date", reverse=True)
            if done:
                record.last_visit_days = (today - done[0].appointment_date).days
            else:
                record.last_visit_days = 0

    @api.depends("last_visit_days", "state")
    def _compute_overdue_checkup(self):
        # Flag patients who haven't visited in over 90 days and are still active
        for record in self:
            record.overdue_checkup = (
                record.last_visit_days > 90
                and record.state not in ("inactive", "recovered")
            )

    @api.depends(
        "age",
        "chronic_condition_ids",
        "chronic_condition_ids.severity",
        "missed_appointments",
        "last_visit_days",
    )
    def _compute_risk_score(self):
        # Severity-weighted points — severe conditions score higher than mild ones
        severity_points = {"severe": 15, "moderate": 10, "mild": 5}
        for record in self:
            score = 0
            # Age factor — max 25 pts
            score += min(record.age // 2, 25)
            # Chronic conditions — weighted by severity (severe=15, moderate=10, mild=5), max 40 pts
            condition_score = sum(
                severity_points.get(c.severity, 10) for c in record.chronic_condition_ids
            )
            score += min(condition_score, 40)
            # Days since last visit — max 20 pts
            score += min(record.last_visit_days // 10, 20)
            # Missed appointments — 5 pts each, max 25
            score += min(record.missed_appointments * 5, 25)

            record.risk_score = min(score, 100)

            if score >= 70:
                record.risk_level = "critical"
            elif score >= 45:
                record.risk_level = "high"
            elif score >= 25:
                record.risk_level = "moderate"
            else:
                record.risk_level = "low"

    # ── Constraints ────────────────────────────────────────────────────────────
    _sql_constraints = [
        (
            "check_patient_age",
            "CHECK(age > 0 AND age <= 120)",
            "Patient age must be between 1 and 120.",
        ),
    ]

    @api.constrains("age")
    def _check_valid_age(self):
        for record in self:
            if record.age <= 0 or record.age > 120:
                raise ValidationError("Age must be between 1 and 120.")

    # ── Business Logic ─────────────────────────────────────────────────────────
    def action_mark_critical(self):
        for record in self:
            if record.state == "recovered":
                raise UserError("A recovered patient cannot be marked critical directly. Please review.")
            record.state = "critical"

    def action_mark_recovered(self):
        for record in self:
            if record.state == "inactive":
                raise UserError("An inactive patient record cannot be marked recovered.")
            record.state = "recovered"

    def action_mark_inactive(self):
        for record in self:
            record.state = "inactive"

    def action_view_appointments(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Appointments",
            "res_model": "clinic.appointment",
            "view_mode": "list,form",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id},
        }

    # ── Cron Method ────────────────────────────────────────────────────────────
    @api.model
    def action_cron_flag_critical(self):
        """
        Runs every night via ir.cron.
        Finds all active patients whose computed risk_score >= 70
        and sets their state to 'critical' automatically.
        """
        critical_patients = self.search([
            ("risk_score", ">=", 70),
            ("state", "=", "active"),
        ])
        for patient in critical_patients:
            patient.state = "critical"
            patient.message_post(
                body="Automatically flagged as Critical by ClinicIQ nightly risk scan. "
                     "Risk score: %d/100." % patient.risk_score
            )