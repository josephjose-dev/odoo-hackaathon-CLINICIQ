from odoo import models, fields


class ClinicCondition(models.Model):
    _name = "clinic.condition"
    _description = "Chronic Medical Condition"

    # SQL constraint: teacher session 4 — unique names like property type names
    _sql_constraints = [
        ("unique_condition_name", "UNIQUE(name)", "A medical condition name must be unique."),
    ]

    name = fields.Char(required=True)
    severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
        default="mild",
    )
