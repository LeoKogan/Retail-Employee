# Set payroll_period from Time Out date (single source of truth for period on save)
try:
    if not doc.time_out:
        frappe.throw(\"Time Out is required to assign a Payroll Period\")

    shift_date = frappe.utils.getdate(doc.time_out)
    periods = frappe.db.get_all(
        \"Payroll Period\",
        filters={\"start_date\": [\"<=\", shift_date], \"end_date\": [\">=\", shift_date]},
        fields=[\"name\"],
        pluck=\"name\",
    )
    if not periods:
        frappe.throw(\"No Payroll Period found for date {0}\".format(shift_date))
    if len(periods) > 1:
        frappe.logger(\"crafted_store_schedule\").warning(
            \"Multiple Payroll Periods for %s: %s — using %s\" % (shift_date, periods, periods[0])
        )
    doc.payroll_period = periods[0]
except Exception:
    frappe.log_error(
        title=\"Assign Payroll Period to Shift\",
        message=frappe.get_traceback()
        + \"
Doc: \"
        + str(getattr(doc, \"name\", None))
        + \"
time_out=\"
        + str(getattr(doc, \"time_out\", None)),
    )
    raise
