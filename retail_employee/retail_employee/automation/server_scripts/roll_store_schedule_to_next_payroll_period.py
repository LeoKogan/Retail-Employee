# Roll Store Schedule into the next payroll period when that period has no shifts.
# Runs daily. Safe to re-run: does nothing if next already has rows, or current has none.
# payroll_period is set by Before Save script \"Assign Payroll Period to Shift\".

try:
    today = frappe.utils.today()

    current_list = frappe.get_all(
        \"Payroll Period\",
        filters={\"start_date\": [\"<=\", today], \"end_date\": [\">=\", today]},
        fields=[\"name\", \"start_date\", \"end_date\"],
        order_by=\"start_date desc\",
        limit_page_length=1,
    )
    if not current_list:
        frappe.log_error(
            title=\"Store Schedule Roll Forward\",
            message=\"No payroll period covers %s\" % today,
        )
    else:
        current = current_list[0]
        current_name = current.get(\"name\")
        current_end = current.get(\"end_date\")
        current_start = current.get(\"start_date\")

        next_list = frappe.get_all(
            \"Payroll Period\",
            filters={\"start_date\": [\">\", current_end]},
            fields=[\"name\", \"start_date\", \"end_date\"],
            order_by=\"start_date asc\",
            limit_page_length=1,
        )
        if not next_list:
            frappe.log_error(
                title=\"Store Schedule Roll Forward\",
                message=\"No next Payroll Period after %s (end %s)\" % (current_name, current_end),
            )
        else:
            nxt = next_list[0]
            nxt_name = nxt.get(\"name\")
            nxt_start = nxt.get(\"start_date\")
            next_count = frappe.db.count(
                \"Store Schedule\", {\"payroll_period\": nxt_name}
            )
            if next_count:
                pass  # already seeded
            else:
                source_names = frappe.get_all(
                    \"Store Schedule\",
                    filters={\"payroll_period\": current_name},
                    pluck=\"name\",
                )
                if not source_names:
                    pass
                else:
                    day_offset = frappe.utils.date_diff(nxt_start, current_start)
                    copy_fields = [
                        \"outlet_name\",
                        \"outlet_color\",
                        \"role\",
                        \"expected_work_hours\",
                        \"employee\",
                        \"prefered_name\",
                        \"employee_email\",
                        \"assigned\",
                        \"color\",
                        \"calendar_text\",
                        \"published\",
                    ]
                    created = 0
                    for src_name in source_names:
                        src = frappe.get_doc(\"Store Schedule\", src_name)
                        new = frappe.new_doc(\"Store Schedule\")
                        for field in copy_fields:
                            new.set(field, src.get(field))
                        new.time_in = frappe.utils.add_to_date(src.time_in, days=day_offset)
                        new.time_out = frappe.utils.add_to_date(src.time_out, days=day_offset)
                        new.insert(ignore_permissions=True)
                        created += 1
                    frappe.msgprint(
                        msg=\"Roll Store Schedule: copied %s shift(s) from %s to %s (+%s days)\"
                        % (created, current_name, nxt_name, day_offset)
                    )
except Exception as e:
    # get_traceback is NOT available inside Server Script safe_exec
    frappe.log_error(
        title=\"Store Schedule Roll Forward\",
        message=str(e),
    )
