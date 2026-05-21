{
    'name': 'CRM Mobile UI',
    'version': '17.0.1.0.2',
    'category': 'Sales/CRM',
    'summary': 'Configure mobile CRM app screens (list, detail, form)',
    'description': """
        Server-side layout configuration for the Flutter CRM mobile app.
        Define sections and fields per model and screen type.
    """,
    'author': 'Tasco',
    'depends': ['base', 'web', 'crm', 'mail'],
    'data': [
        'security/mobile_ui_security.xml',
        'security/ir.model.access.csv',
        'views/mobile_ui_layout_views.xml',
        'views/menu.xml',
        'data/crm_lead_default_layouts.xml',
        'data/crm_lead_detail_marketing_sync.xml',
        'data/crm_lead_detail_address_sync.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
