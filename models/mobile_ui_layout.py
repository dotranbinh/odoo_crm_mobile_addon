from odoo import api, fields, models


class MobileUiLayout(models.Model):
    _name = 'mobile.ui.layout'
    _description = 'Mobile UI Layout'
    _order = 'model_name, screen, sequence, id'

    name = fields.Char(required=True)
    model_name = fields.Char(string='Model', required=True, index=True)
    screen = fields.Selection(
        selection=[
            ('list', 'List'),
            ('detail', 'Detail'),
            ('form', 'Form (Edit)'),
        ],
        required=True,
        index=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company')
    version = fields.Integer(default=1, readonly=True)
    sequence = fields.Integer(default=10)
    other_info_title = fields.Char(
        string='Other Info Title',
        default='Other Information',
        translate=True,
    )
    include_custom_fields = fields.Boolean(
        string='Include Custom Fields (x_*)',
        default=True,
        help='Append x_* / x_studio_* fields not listed below into an Other Info section.',
    )
    section_ids = fields.One2many(
        'mobile.ui.section',
        'layout_id',
        string='Sections',
    )
    preview_json = fields.Text(
        string='Preview JSON',
        compute='_compute_preview_json',
    )

    @api.depends('section_ids', 'section_ids.field_ids', 'version')
    def _compute_preview_json(self):
        import json
        for layout in self:
            try:
                data = layout._build_mobile_layout_payload()
                layout.preview_json = json.dumps(data, indent=2, ensure_ascii=False)
            except Exception as e:
                layout.preview_json = str(e)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.active:
                rec._deactivate_siblings()
        return records

    def write(self, vals):
        bump_version = any(
            k in vals
            for k in ('section_ids', 'include_custom_fields', 'other_info_title', 'model_name', 'screen')
        )
        if bump_version:
            for rec in self:
                vals = dict(vals, version=rec.version + 1)
                break
        res = super().write(vals)
        if vals.get('active'):
            self._deactivate_siblings()
        return res

    def _deactivate_siblings(self):
        for layout in self:
            domain = [
                ('id', '!=', layout.id),
                ('model_name', '=', layout.model_name),
                ('screen', '=', layout.screen),
                ('active', '=', True),
            ]
            if layout.company_id:
                domain.append(('company_id', '=', layout.company_id.id))
            else:
                domain.append(('company_id', '=', False))
            siblings = self.search(domain)
            if siblings:
                siblings.write({'active': False})

    def action_set_active(self):
        self.ensure_one()
        self._deactivate_siblings()
        self.write({'active': True})

    def action_duplicate(self):
        self.ensure_one()
        new_layout = self.copy({
            'name': f'{self.name} (copy)',
            'active': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mobile.ui.layout',
            'res_id': new_layout.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def get_mobile_layout(self, model_name, screen, company_id=None, lang=None):
        """Public API for Flutter app. Returns JSON-serializable layout dict."""
        # Read-only sudo so any authenticated mobile user can load layout.
        return self.sudo()._get_mobile_layout_impl(model_name, screen, company_id, lang)

    @api.model
    def _get_mobile_layout_impl(self, model_name, screen, company_id=None, lang=None):
        layout = self._find_active_layout(model_name, screen, company_id)
        if not layout:
            return {
                'version': 0,
                'model': model_name,
                'screen': screen,
                'other_info_title': 'Other Information',
                'include_custom_fields': False,
                'sections': [],
            }
        return layout._build_mobile_layout_payload(lang=lang)

    def _find_active_layout(self, model_name, screen, company_id=None):
        domain = [
            ('model_name', '=', model_name),
            ('screen', '=', screen),
            ('active', '=', True),
        ]
        if company_id:
            layout = self.search(domain + [('company_id', '=', company_id)], limit=1)
            if layout:
                return layout
        return self.search(domain + [('company_id', '=', False)], limit=1)

    def _build_mobile_layout_payload(self, lang=None):
        self.ensure_one()
        Model = self.env[self.model_name]
        fields_meta = Model.fields_get(
            attributes=['string', 'type', 'selection', 'relation', 'readonly', 'required'],
        )

        configured_names = set()
        sections = []

        for section in self.section_ids.sorted('sequence'):
            fields_payload = []
            for field_line in section.field_ids.sorted('sequence'):
                name = field_line.field_name
                if name not in fields_meta:
                    continue
                meta = fields_meta[name]
                configured_names.add(name)
                fields_payload.append(self._field_to_json(field_line, meta))

            if fields_payload:
                sections.append({
                    'key': f'section_{section.id}',
                    'title': section.name,
                    'sequence': section.sequence,
                    'collapsed': section.collapsed,
                    'fields': fields_payload,
                })

        if self.include_custom_fields:
            custom_fields = []
            for fname, meta in sorted(fields_meta.items()):
                if fname in configured_names:
                    continue
                if not self._is_custom_field(fname):
                    continue
                if not self._is_displayable_field(fname, meta):
                    continue
                custom_fields.append(self._field_to_json_from_meta(fname, meta))

            if custom_fields:
                sections.append({
                    'key': 'other_info',
                    'title': self.other_info_title or 'Other Information',
                    'sequence': 9999,
                    'collapsed': False,
                    'fields': custom_fields,
                })

        sections.sort(key=lambda s: s['sequence'])

        return {
            'version': self.version,
            'model': self.model_name,
            'screen': self.screen,
            'other_info_title': self.other_info_title or 'Other Information',
            'include_custom_fields': self.include_custom_fields,
            'sections': sections,
        }

    @api.model
    def _field_to_json(self, field_line, meta):
        widget = field_line.widget
        if widget == 'text' and meta.get('type') == 'many2one':
            widget = 'many2one'
        return {
            'name': field_line.field_name,
            'label': field_line.label or meta.get('string') or field_line.field_name,
            'type': self._map_odoo_type(meta.get('type')),
            'widget': widget,
            'relation': meta.get('relation') or False,
            'readonly': field_line.readonly or bool(meta.get('readonly')),
            'required': field_line.required,
            'show_if_empty': field_line.show_if_empty,
            'copyable': field_line.copyable,
            'list_primary': field_line.list_primary,
            'list_subtitle': field_line.list_subtitle,
            'selection': meta.get('selection') or [],
        }

    @api.model
    def _field_to_json_from_meta(self, fname, meta):
        ftype = meta.get('type') or 'char'
        widget = self._default_widget_for_type(ftype, fname)
        return {
            'name': fname,
            'label': meta.get('string') or fname,
            'type': self._map_odoo_type(ftype),
            'widget': widget,
            'relation': meta.get('relation') or False,
            'readonly': bool(meta.get('readonly')),
            'required': bool(meta.get('required')),
            'show_if_empty': False,
            'copyable': widget in ('phone', 'email'),
            'list_primary': False,
            'list_subtitle': False,
            'selection': meta.get('selection') or [],
        }

    @staticmethod
    def _map_odoo_type(odoo_type):
        mapping = {
            'monetary': 'float',
            'html': 'text',
        }
        return mapping.get(odoo_type, odoo_type or 'char')

    @staticmethod
    def _default_widget_for_type(ftype, fname):
        if 'phone' in fname:
            return 'phone'
        if 'email' in fname:
            return 'email'
        if fname == 'stage_id':
            return 'stage'
        if fname == 'priority':
            return 'priority'
        if ftype == 'many2one':
            return 'many2one'
        if ftype == 'boolean':
            return 'boolean'
        if ftype == 'date':
            return 'date'
        if ftype == 'datetime':
            return 'datetime'
        if ftype in ('monetary', 'float', 'integer'):
            return 'currency' if ftype == 'monetary' else 'number'
        if ftype == 'html':
            return 'html'
        if ftype == 'selection':
            return 'selection'
        return 'text'

    @staticmethod
    def _is_custom_field(name):
        return name.startswith('x_') or name.startswith('x_studio_')

    @staticmethod
    def _is_displayable_field(name, meta):
        excluded_types = {'one2many', 'many2many', 'binary', 'image', 'reference', 'properties'}
        excluded_names = {
            'message_ids', 'activity_ids', 'display_name', '__last_update',
        }
        if name in excluded_names:
            return False
        if name.startswith('message_') and name.endswith('_ids'):
            return False
        return meta.get('type') not in excluded_types
