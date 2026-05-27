# CRM Mobile UI (Odoo 17 addon)

Configure Flutter CRM mobile screens: **list**, **detail**, and **form** per model.

## Install on `tascort_dev_8`

1. Copy `crm_mobile_ui` into your Odoo `addons_path`.
2. Restart Odoo, update Apps list.
3. Install **CRM Mobile UI**.
4. Open **CRM → Configuration → Mobile App UI** and adjust layouts.
5. Assign **Mobile UI / Manager** to admins who edit layouts.

## Mobile API

Model: `mobile.ui.layout`  
Method: `get_mobile_layout(model_name, screen, company_id=None, lang=None)`

- `screen`: `list` | `detail` | `form`
- Returns `{ version, model, screen, sections[], ... }`
- `version: 0` + empty `sections` → app falls back to `get_views` XML parser

### JSON-RPC example

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "tascort_dev_8",
      "<uid>",
      "<password>",
      "mobile.ui.layout",
      "get_mobile_layout",
      ["crm.lead", "detail"],
      {}
    ]
  },
  "id": 1
}
```

## Default data

On install, creates active layouts for `crm.lead` list, detail, and form with sensible default fields.
