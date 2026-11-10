# Store Schedule Lock Past Shifts (Delete)  -- DocType Event: Before Delete
# Approved by Leo 2026-11-09. Shifts whose Alberta date is before today can't be deleted,
# except by a System Manager. Doctype name kept in one place for the Nov 10 rename.
SCHEDULE_DT = "Store Schedule"
LOCK_MSG = "Past shifts are locked. Ask a System Manager."

# frappe.get_roles() isn't available to Server Scripts here, so read Has Role directly.
is_system_manager = frappe.session.user == "Administrator" or bool(frappe.db.exists(
    "Has Role", {"parent": frappe.session.user, "parenttype": "User", "role": "System Manager"}))

if not is_system_manager:
    today = frappe.utils.getdate(frappe.utils.nowdate())
    orig_time_in = frappe.db.get_value(SCHEDULE_DT, doc.name, "time_in") or doc.time_in
    if orig_time_in and frappe.utils.getdate(orig_time_in) < today:
        frappe.throw(LOCK_MSG, title="Shift locked")
