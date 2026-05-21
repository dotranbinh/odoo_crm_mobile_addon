# Mobile UI layout reference (JSON)

Full layouts returned by `mobile.ui.layout.get_mobile_layout()` for **crm.lead**.

| File | Screen | Purpose |
|------|--------|---------|
| `mobile_ui_crm_lead_detail_full.json` | `detail` | Read-only lead/opportunity detail (all main Odoo 17 CRM fields) |
| `mobile_ui_crm_lead_form_full.json` | `form` | Edit lead/opportunity (writable subset) |

## Sections (standard Odoo CRM)

1. **Contact Information** — `partner_name`, `contact_name`, `title`, `email_from`, `phone`, `mobile`, `website`, `function`, `partner_id` (detail)
2. **Address** — `street`, `street2`, `city`, `zip`, `state_id`, `country_id`
3. **Opportunity** — `name`, `type`, `stage_id`, `priority`, `expected_revenue`, `probability`, `date_deadline`, `date_open`, `date_closed`, `lost_reason_id`
4. **Marketing** — `source_id`, `medium_id`, `campaign_id`, `referred`
5. **Sales** — `user_id`, `team_id`, `company_id` (detail)
6. **Notes** — `description`

## Not included (mobile app limits)

- `tag_ids` (many2many)
- Chatter / `message_*` / `activity_*` fields
- One2many lines (orders, meetings, etc.)

## Use in Odoo

Import manually via **Mobile App UI** preview, or extend `data/crm_lead_default_layouts.xml` from these files.

## Use in Flutter (mock)

Copy to `crm_app/assets/mock/mobile_ui_crm_lead_detail.json` and `mobile_ui_crm_lead_form.json`.

After changing layout on server, **logout/login** on the app to clear in-memory layout cache.
