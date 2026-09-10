# Retail Employee

Frappe app for Crafted **staff / employee portal**.

## Includes
- `/staff` landing (this app only — not in Consignor)
- **Web Pages:** manage-shifts, my-shifts, my-tasks, cashier-close, sales-goals
- **Web Forms:** block-time-off, employee-clock-in-out
- **DocTypes** (no `CRAFTED ` prefix): Outlets, Store Schedule, Employee Info, Store Roles, Sales Targets/Commissions, Register Closure, Rooster Schedule, Store Shift Type/Assignment, …
- **Automation sources:** Server Scripts, Client Scripts, Notifications from erp.craftedgoods.ca (`retail_employee/automation/`)
- **Live hooks:** clock-in/out SMS on `Employee Checkin` after_insert; Store Schedule Desk JS

## DocType rename
Production used `CRAFTED …` names. In this app the prefix is removed.  
HRMS already owns `Shift Type` / `Shift Assignment`, so those become **Store Shift Type** / **Store Shift Assignment**.

## Install
```bash
bench get-app https://github.com/LeoKogan/Retail-Employee.git
bench --site <site> install-app retail_employee
bench --site <site> migrate
```
