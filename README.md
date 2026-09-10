# Retail Employee

Frappe app for Crafted staff / employee portal (website).

Includes:
- `/staff` landing
- Web Pages: Manage Shifts, My Tasks, Cashier Close, Sales Goals
- Web Forms: Block Time Off, Employee Clock In/Out
- CRAFTED DocTypes used by those pages (Outlets, Store Schedule, Employee Info, etc.)
- Server Script source for clock-in/out SMS (deploy on site as Server Script)

Install on a bench:
```
bench get-app /path/to/Retail-Employee
# or: bench get-app https://github.com/LeoKogan/Retail-Employee.git
bench --site <site> install-app retail_employee
bench --site <site> migrate
```
