# Staff automation + portal sources

## Included
- **Web Pages** (`../web_page/`): manage-shifts, my-shifts, my-tasks, cashier-close, sales-goals
- **Web Forms** (`../web_form/`): block-time-off, employee-clock-in-out
- **www/staff**: staff landing (only in this app)
- **Server Scripts** (`server_scripts/`): staff clock/schedule/commission/register logic from erp.craftedgoods.ca
- **Client Scripts** (`client_scripts/`): Store Schedule form, commissions/timesheet helpers
- **Notifications** (`notifications/`): shift assigned, register discrepancy, hours mismatch; Clock Punch disabled (SMS ported to Python)

## How functionality runs
1. Clock SMS: `retail_employee.events.employee_checkin.after_insert` (hooks `doc_events`)
2. Store Schedule Desk JS: `doctype_js` → `public/js/store_schedule.js`
3. Other Server Scripts / Notifications: source in this folder — import to Desk or port into `events/` / fixtures

## DocType rename
`CRAFTED …` prefix removed. HRMS collisions → `Store Shift Type`, `Store Shift Assignment`.

## Prod vs testing (local) variants of Server Scripts
- `server_scripts/*.py|json` are **prod-shaped** (erp.craftedgoods.ca, `CRAFTED …` DocTypes).
- `server_scripts_local/` holds the **testing** variants (crafted.localhost, un-prefixed DocTypes:
  `Store Schedule`, `Timesheets`, `Employee Info`; links to `http://crafted.localhost:8000`).
  Regenerate with `python3 make_local_variants.py` after changing a prod script; do not hand-edit.
  Currently ported: Create Time Sheet for Employee, Clock Out Employee After shift is over,
  Alert shop@ on Missed Clock-In, Alert Missed Schedule Clock In (disabled).
- Install on the testing site (never prod): `bench set-config -g server_script_enabled 1`, copy
  `server_scripts_local/*.json` into the container and run `install_local_server_scripts.install`
  (see its docstring).
- The local app has no `Timesheets` DocType yet (prod `CRAFTED Timesheets`/`CRAFTED Timesheet Detail`;
  `Timesheet Detail` collides with ERPNext), so the local Create Time Sheet variant is a no-op until
  that DocType exists.
