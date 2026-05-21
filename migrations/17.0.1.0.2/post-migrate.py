"""Bump lead detail/form layout version after Address section sync."""


def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """
        UPDATE mobile_ui_layout
        SET version = version + 1
        WHERE id IN (
            SELECT res_id
            FROM ir_model_data
            WHERE module = 'crm_mobile_ui'
              AND name IN ('layout_crm_lead_detail', 'layout_crm_lead_form')
        )
        """
    )
