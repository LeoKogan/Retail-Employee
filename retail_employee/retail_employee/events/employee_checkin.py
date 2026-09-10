"""Employee Checkin events for Retail Employee."""

import frappe


def after_insert(doc, method=None):
    """SMS employee cell_number on clock IN/OUT."""
    if not doc.employee:
        frappe.log_error("Clock SMS: missing employee on " + str(doc.name), "Employee Clock SMS")
        return

    emp = frappe.get_doc("Employee", doc.employee)
    raw = (emp.cell_number or "").strip()
    digits = "".join(ch for ch in raw if ch.isdigit())
    phone = None
    if digits:
        if len(digits) == 10:
            digits = "1" + digits
        phone = "+" + digits

    if not phone:
        frappe.log_error(
            "Clock SMS: no cell_number for {0} ({1})".format(emp.name, emp.employee_name),
            "Employee Clock SMS",
        )
        return

    log_type = (doc.log_type or "").upper()
    when = doc.time or frappe.utils.now_datetime()
    message = (
        "Hello {0},\n"
        "You successfully clocked {1} at {2}.\n"
        "— Crafted time clock"
    ).format(emp.employee_name, log_type, when)

    try:
        from frappe.core.doctype.sms_settings.sms_settings import send_sms
        send_sms([phone], message)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Employee Clock SMS")
