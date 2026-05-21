from odoo import api, fields, models


class MobileUiField(models.Model):
    _name = 'mobile.ui.field'
    _description = 'Mobile UI Field'
    _order = 'sequence, id'

    section_id = fields.Many2one(
        'mobile.ui.section',
        string='Section',
        required=True,
        ondelete='cascade',
    )
    field_name = fields.Char(string='Field Name', required=True)
    label = fields.Char(string='Label Override')
    sequence = fields.Integer(default=10)
    widget = fields.Selection(
        selection=[
            ('text', 'Text'),
            ('phone', 'Phone'),
            ('email', 'Email'),
            ('url', 'URL'),
            ('date', 'Date'),
            ('datetime', 'Date Time'),
            ('boolean', 'Boolean'),
            ('selection', 'Selection'),
            ('many2one', 'Many2one'),
            ('number', 'Number'),
            ('currency', 'Currency'),
            ('html', 'HTML'),
            ('priority', 'Priority'),
            ('stage', 'Stage'),
        ],
        string='Widget',
        default='text',
        required=True,
    )
    readonly = fields.Boolean(default=False)
    required = fields.Boolean(default=False)
    show_if_empty = fields.Boolean(string='Show If Empty', default=False)
    copyable = fields.Boolean(default=False)
    list_primary = fields.Boolean(string='List Primary', default=False)
    list_subtitle = fields.Boolean(string='List Subtitle', default=False)

    @api.constrains('field_name', 'section_id')
    def _check_field_exists(self):
        for record in self:
            if not record.section_id or not record.field_name:
                continue
            model_name = record.section_id.layout_id.model_name
            field = self.env['ir.model.fields'].search([
                ('model', '=', model_name),
                ('name', '=', record.field_name),
            ], limit=1)
            if not field:
                from odoo.exceptions import ValidationError
                raise ValidationError(
                    f"Field '{record.field_name}' does not exist on model '{model_name}'."
                )
