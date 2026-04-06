from odoo import models, fields


class ClinicMedicine(models.Model):
    _name = "clinic.medicine"
    _description = "Medicine"

    # SQL constraint: medicine names must be unique for allergy checking to work correctly
    _sql_constraints = [
        ("unique_medicine_name", "UNIQUE(name)", "A medicine name must be unique."),
    ]

    name = fields.Char(required=True)
    category = fields.Char()
