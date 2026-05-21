from odoo import fields, models


class MobileUiSection(models.Model):
    _name = 'mobile.ui.section'
    _description = 'Mobile UI Section'
    _order = 'sequence, id'

    layout_id = fields.Many2one(
        'mobile.ui.layout',
        string='Layout',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Title', required=True, translate=True)
    sequence = fields.Integer(default=10)
    collapsed = fields.Boolean(default=False)
    field_ids = fields.One2many(
        'mobile.ui.field',
        'section_id',
        string='Fields',
    )
