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

## Prod and testing share DocType names
- Production (erp.craftedgoods.ca) dropped the `CRAFTED ` DocType prefix on 2026-11-09 (e.g. `Store Schedule`,
  `Timesheets`, `Timesheets Detail`, `Employee Info`, `Store Payments`), so prod and the app use the same names.
- `server_scripts/`, `client_scripts/`, `notifications/` and `../web_page/` are exported from production
  (production is the source of truth). Some record names keep `CRAFTED` (e.g. the Server Script
  "CRAFTED Sales Commissions Hourly Calculation", Report "CRAFTED Payroll Report"); only DocTypes were renamed.
- The separate `server_scripts_local/` variants and `make_local_variants.py` are gone. To load a script on a
  testing site (never prod): `bench set-config -g server_script_enabled 1`, copy `server_scripts/<slug>.json`
  into the container and run `install_local_server_scripts.install` (see its docstring). Links in the scripts
  point at erp.craftedgoods.ca.

## Custom Fields
- `custom_fields/employee_checkin_store_schedule.json`: read-only Link `Employee Checkin.store_schedule` -> `Store Schedule`,
  set on insert by the Server Script "Employee Checkin Use Server Time" (added 2026-11-09; 4,433 past punches backfilled).
