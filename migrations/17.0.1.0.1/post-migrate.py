"""Bump detail layout version after marketing field sync so mobile clients reload layout."""


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
              AND name = 'layout_crm_lead_detail'
        )
        """
    )
