from odoo import models, fields


class ClinicAllergy(models.Model):
    _name = "clinic.allergy"
    _description = "Patient Allergy"

    # SQL constraint: mirrors teacher's estate.property.tag unique constraint
    _sql_constraints = [
        ("unique_allergy_name", "UNIQUE(name)", "An allergy name must be unique."),
    ]

    name = fields.Char(required=True)
