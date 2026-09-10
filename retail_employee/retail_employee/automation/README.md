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
