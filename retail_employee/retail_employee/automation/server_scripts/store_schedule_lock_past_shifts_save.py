# Store Schedule Lock Past Shifts (Save)  -- DocType Event: Before Save
# Approved by Leo 2026-11-09. Shifts whose Alberta date (system TZ America/Edmonton) is before
# today are locked: they can't be edited, and new shifts can't be created/moved into the past.
# Only System Manager may bypass. Doctype name kept in one place for the Nov 10 rename.
SCHEDULE_DT = "Store Schedule"
LOCK_MSG = "Past shifts are locked. Ask a System Manager."

# frappe.get_roles() isn't available to Server Scripts here, so read Has Role directly.
is_system_manager = frappe.session.user == "Administrator" or bool(frappe.db.exists(
    "Has Role", {"parent": frappe.session.user, "parenttype": "User", "role": "System Manager"}))

if not is_system_manager:
    today = frappe.utils.getdate(frappe.utils.nowdate())
    if not doc.is_new():
        orig_time_in = frappe.db.get_value(SCHEDULE_DT, doc.name, "time_in")
        if orig_time_in and frappe.utils.getdate(orig_time_in) < today:
            frappe.throw(LOCK_MSG, title="Shift locked")
    if doc.time_in and frappe.utils.getdate(doc.time_in) < today:
        if doc.is_new():
            frappe.throw("You can't create a shift on a past date. " + LOCK_MSG, title="Shift locked")
        frappe.throw("You can't move a shift to a past date. " + LOCK_MSG, title="Shift locked")
