# Alert shop@ on Missed Clock-In (Scheduler Event, cron */5 7-20 * * *)
# For each CRAFTED Store Schedule shift today that started 15+ minutes ago and has not
# ended, if the (Active) employee has no Employee Checkin IN between (time_in - 60 min)
# and now, email shop@craftedgoods.ca once. Staff are NOT emailed / SMS'd here.
# Dedupe: an Info Comment "MISSED-CLOCK-IN-ALERT" is added on the schedule doc after the
# alert is queued; shifts that already have that comment are skipped.
# Skips employees that are not Active and employees with approved Leave on that date.

SHOP_EMAIL = "shop@craftedgoods.ca"
GRACE_MIN = 15
IN_LOOKBACK_MIN = 60
DEDUPE_TAG = "MISSED-CLOCK-IN-ALERT"

try:
    now = frappe.utils.now_datetime()
    today = frappe.utils.getdate(now)
    day_start = frappe.utils.get_datetime(str(today) + " 00:00:00")
    started_before = frappe.utils.add_to_date(now, minutes=-GRACE_MIN)

    shifts = frappe.db.get_all(
        "CRAFTED Store Schedule",
        filters=[
            ["time_in", ">=", day_start],
            ["time_in", "<=", started_before],
            ["time_out", ">", now],
            ["employee", "is", "set"],
            ["docstatus", "<", 2],
        ],
        fields=["name", "employee", "prefered_name", "outlet_name", "role", "time_in", "time_out"],
        order_by="time_in",
    )

    for shift in shifts:
        try:
            emp = shift.employee
            if frappe.db.get_value("Employee", emp, "status") != "Active":
                continue
            if frappe.db.exists("Comment", {
                "reference_doctype": "CRAFTED Store Schedule",
                "reference_name": shift.name,
                "comment_type": "Info",
                "content": ["like", DEDUPE_TAG + "%"],
            }):
                continue
            in_from = frappe.utils.add_to_date(shift.time_in, minutes=-IN_LOOKBACK_MIN)
            if frappe.db.exists("Employee Checkin", {
                "employee": emp,
                "log_type": "IN",
                "time": ["between", [in_from, now]],
            }):
                continue
            if frappe.db.exists("Leave Application", {
                "employee": emp,
                "status": "Approved",
                "docstatus": 1,
                "from_date": ["<=", today],
                "to_date": [">=", today],
            }):
                continue

            emp_name = frappe.db.get_value("Employee", emp, "employee_name") or shift.prefered_name or emp
            outlet = shift.outlet_name or "(no store set)"
            t_in = frappe.utils.format_datetime(shift.time_in, "EEE MMM d, h:mm a")
            t_out = frappe.utils.format_datetime(shift.time_out, "h:mm a")
            subject = "Missed clock-in: " + str(emp_name) + " @ " + str(outlet) + " (" + t_in + ") [" + shift.name + "]"
            message = (
                "<p><b>" + str(emp_name) + "</b> (" + str(emp) + ") has <b>no clock-in " + str(GRACE_MIN)
                + " min after the scheduled start</b>.</p>"
                "<p><b>Store:</b> " + str(outlet) + "<br>"
                "<b>Role:</b> " + str(shift.role or "") + "<br>"
                "<b>Scheduled shift:</b> " + t_in + " – " + t_out + "</p>"
                "<p>Schedule: <a href='https://erp.craftedgoods.ca/app/crafted-store-schedule/" + shift.name + "'>"
                + shift.name + "</a><br>"
                "Checkins: <a href='https://erp.craftedgoods.ca/app/employee-checkin?employee=" + str(emp) + "'>open</a></p>"
            )
            frappe.sendmail(recipients=[SHOP_EMAIL], subject=subject, message=message)
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "CRAFTED Store Schedule",
                "reference_name": shift.name,
                "content": DEDUPE_TAG + ": emailed " + SHOP_EMAIL + " at " + str(now).split(".")[0],
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            frappe.log_error(title="Missed Clock-In alert failed for " + str(shift.name))
except Exception:
    frappe.log_error(title="Alert shop@ on Missed Clock-In")
