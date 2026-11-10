# Employee Clock In-Out Notification — SMS to employee cell_number
# Event: After Insert on Employee Checkin
# safe_exec: no import / no str.format / no get_traceback / no get_attr

if not doc.employee:
    frappe.log_error("Clock SMS: missing employee on " + str(doc.name), "Employee Clock SMS")
else:
    try:
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
                "Clock SMS: no cell_number for " + str(emp.name) + " (" + str(emp.employee_name) + ")",
                "Employee Clock SMS",
            )
        else:
            log_type = (doc.log_type or "").upper()
            when = doc.time or frappe.utils.now_datetime()
            message = (
                "Hello " + str(emp.employee_name) + ",\n"
                "You successfully clocked " + str(log_type) + " at " + str(when) + ".\n"
                "— Crafted time clock"
            )
            frappe.call(
                "frappe.core.doctype.sms_settings.sms_settings.send_sms",
                receiver_list=[phone],
                msg=message,
                success_msg=False,
            )
    except Exception as e:
        frappe.log_error("Clock SMS failed: " + str(e), "Employee Clock SMS")
