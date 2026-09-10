try:
    # =============================================================================
    # Daily Clock Entries Report + Auto Clock-Out
    # =============================================================================
    # Purpose:
    #   Run at end of day. For every employee with clock entries today:
    #     - If they clocked IN but NOT OUT, automatically create a clock-OUT entry
    #       using their scheduled shift end time from Store Schedule
    #       (falling back to the day's end if no shift is found).
    #     - If they're missing a clock IN, flag it in the report (we can't guess
    #       when they actually started).
    #   Then email a daily summary table to CRAFTED.
    # =============================================================================

    # -----------------------------------------------------------------------------
    # Configuration
    # -----------------------------------------------------------------------------
    RECIPIENT_EMAIL = \"shop@craftedgoods.ca\"
    SENDER_EMAIL = \"erp-notifications@craftedgoods.ca\"
    AUTO_DEVICE_ID = \"Automatic Clock out - missed at end of day\"

    # -----------------------------------------------------------------------------
    # Time window: full calendar day (today)
    # -----------------------------------------------------------------------------
    today = frappe.utils.today()
    start_of_day = frappe.utils.add_to_date(today, hours=0,  minutes=0,  seconds=0,  as_datetime=True)
    end_of_day   = frappe.utils.add_to_date(today, hours=23, minutes=59, seconds=59, as_datetime=True)


    # -----------------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------------
    def get_scheduled_clock_out(employee, day_start, day_end):
        \"\"\"
        Look up the employee's scheduled shift end time for today from
        Store Schedule. Returns a datetime or None if no shift is found.

        If the employee has multiple shifts in one day, take the latest time_out
        so we cover their entire workday with one auto clock-out.
        \"\"\"
        shifts = frappe.db.get_all(
            'Store Schedule',
            filters=[
                ['employee', '=', employee],
                ['time_out', '>=', day_start],
                ['time_out', '<=', day_end],
            ],
            fields=['time_out'],
            order_by='time_out desc',
            limit=1,
        )
        return shifts[0]['time_out'] if shifts else None


    def create_auto_clock_out(employee, time):
        \"\"\"Create the missing Employee Checkin (OUT) record.\"\"\"
        frappe.get_doc(dict(
            doctype='Employee Checkin',
            employee=employee,
            time=time,
            log_type='OUT',
            device_id=AUTO_DEVICE_ID,
        )).insert(ignore_permissions=True)


    def fmt_time(dt):
        \"\"\"Format a datetime as HH:MM.\"\"\"
        return frappe.utils.get_datetime(dt).strftime('%H:%M')


    # -----------------------------------------------------------------------------
    # Step 1: Pull today's clock entries
    # -----------------------------------------------------------------------------
    clock_entries = frappe.db.get_all(
        'Employee Checkin',
        filters=[
            ['time', '>=', start_of_day],
            ['time', '<=', end_of_day],
        ],
        fields=['*'],
        order_by='time',
    )

    # -----------------------------------------------------------------------------
    # Step 2: Organize entries by employee
    #
    # For each employee we keep:
    #   - 'IN':  earliest clock-in of the day (or None)
    #   - 'OUT': latest  clock-out of the day (or None)
    #   - 'name', 'logs'
    #
    # Using earliest IN / latest OUT means if someone clocked in/out multiple
    # times we still see the full span of their workday in the summary.
    # -----------------------------------------------------------------------------
    employee_logs = {}
    for entry in clock_entries:
        emp = entry['employee']
        if emp not in employee_logs:
            employee_logs[emp] = {
                'IN':   None,
                'OUT':  None,
                'name': entry['employee_name'],
                'logs': [],
            }

        if entry['log_type'] == 'IN':
            # Keep the earliest IN of the day
            if employee_logs[emp]['IN'] is None or entry['time'] < employee_logs[emp]['IN']['time']:
                employee_logs[emp]['IN'] = entry
        elif entry['log_type'] == 'OUT':
            # Keep the latest OUT of the day
            if employee_logs[emp]['OUT'] is None or entry['time'] > employee_logs[emp]['OUT']['time']:
                employee_logs[emp]['OUT'] = entry

        employee_logs[emp]['logs'].append(entry)

    # -----------------------------------------------------------------------------
    # Step 3: Auto clock-out anyone who clocked IN but never clocked OUT
    #
    # RULE: We only auto-clock-OUT if the employee actually clocked IN today.
    #       If they have no IN entry, we leave it as \"Missing\" in the report —
    #       we won't fabricate a workday for someone who never showed up on
    #       the clock.
    # -----------------------------------------------------------------------------
    auto_clocked_out = []   # list of (name, time, source) for the report

    for emp, logs in employee_logs.items():
        if logs['IN'] is not None and logs['OUT'] is None:
            # Try to use the scheduled shift end time first
            scheduled_out = get_scheduled_clock_out(emp, start_of_day, end_of_day)

            if scheduled_out:
                out_time = scheduled_out
                source = \"scheduled shift end\"
            else:
                # No scheduled shift found — fall back to end of day
                out_time = end_of_day
                source = \"end of day (no shift on schedule)\"

            # Safety: don't clock out BEFORE they clocked in
            if out_time < logs['IN']['time']:
                out_time = logs['IN']['time']
                source += \" (adjusted: was before clock-in)\"

            create_auto_clock_out(emp, out_time)

            # Update the in-memory record so the report shows the new OUT
            logs['OUT'] = {
                'time': out_time,
                'log_type': 'OUT',
                'device_id': AUTO_DEVICE_ID,
            }
            auto_clocked_out.append((logs['name'], out_time, source))


    # -----------------------------------------------------------------------------
    # Step 4: Build the HTML summary table
    # -----------------------------------------------------------------------------
    table_style = \"border-collapse: collapse;\"
    cell_style = \"border: 1px solid #ccc; padding: 6px 10px;\"
    auto_style = \"color: #b25900; background-color: #fff4e0; padding: 4px; border-radius: 3px;\"   # orange-ish to highlight auto-generated entries
    miss_style = \"color: red; text-align: center;\"

    complete_logs_table = (
        f\"<table style='{table_style}'>\"
        f\"<tr>\"
        f\"<th style='{cell_style}'>Employee</th>\"
        f\"<th style='{cell_style}'>IN</th>\"
        f\"<th style='{cell_style}'>OUT</th>\"
        f\"</tr>\"
    )

    for emp, logs in employee_logs.items():
        complete_logs_table += f\"<tr><td style='{cell_style}'>{logs['name']}</td>\"

        # IN cell
        if logs['IN'] is not None:
            complete_logs_table += f\"<td style='{cell_style}'>{fmt_time(logs['IN']['time'])}</td>\"
        else:
            complete_logs_table += (
                f\"<td style='{cell_style}'>\"
                f\"<div style='{miss_style}'>\"
                f\"<a href='https://erp.craftedgoods.ca/app/employee-checkin/'>Missing</a>\"
                f\"</div></td>\"
            )

        # OUT cell:
        #   - real clock-out:        plain time
        #   - auto-generated OUT:    time + \"Automated Clock Out\" label, highlighted
        #   - no OUT (and no IN):    \"Missing\" link (we did NOT auto-clock-out
        #                            because the employee never clocked IN)
        if logs['OUT'] is not None:
            is_auto = logs['OUT'].get('device_id') == AUTO_DEVICE_ID
            time_str = fmt_time(logs['OUT']['time'])
            if is_auto:
                complete_logs_table += (
                    f\"<td style='{cell_style}'>\"
                    f\"<div style='{auto_style}'>\"
                    f\"<b>{time_str}</b><br>\"
                    f\"<small>Automated Clock Out</small>\"
                    f\"</div></td>\"
                )
            else:
                complete_logs_table += f\"<td style='{cell_style}'>{time_str}</td>\"
        else:
            complete_logs_table += (
                f\"<td style='{cell_style}'>\"
                f\"<div style='{miss_style}'>\"
                f\"<a href='https://erp.craftedgoods.ca/app/employee-checkin/'>Missing</a>\"
                f\"</div></td>\"
            )

        complete_logs_table += \"</tr>\"

    complete_logs_table += \"</table>\"


    # -----------------------------------------------------------------------------
    # Step 5: Scheduled no-shows (assigned today, no clock-IN)
    # -----------------------------------------------------------------------------
    scheduled_today = frappe.db.get_all(
        \"Store Schedule\",
        filters=[
            [\"time_in\", \">=\", start_of_day],
            [\"time_in\", \"<=\", end_of_day],
            [\"employee\", \"is\", \"set\"],
            [\"assigned\", \"=\", 1],
        ],
        fields=[\"employee\", \"prefered_name\", \"outlet_name\", \"time_in\", \"employee_email\", \"name\"],
        order_by=\"time_in\",
    )
    scheduled_no_show = []
    seen_emp = set()
    for sh in scheduled_today:
        emp = sh.get(\"employee\")
        if not emp or emp in seen_emp:
            continue
        logs = employee_logs.get(emp)
        if logs is None or logs.get(\"IN\") is None:
            scheduled_no_show.append(sh)
            seen_emp.add(emp)

    # -----------------------------------------------------------------------------
    # Step 6: Build and send the email
    # -----------------------------------------------------------------------------
    missing_in_employees = [
        logs[\"name\"] for logs in employee_logs.values() if logs[\"IN\"] is None
    ]

    subject = \"Daily Clock Entries\"
    message = \"\"

    if auto_clocked_out:
        message += \"<b>Auto clock-out applied to the following employees:</b><br>\"
        for name, out_time, source in auto_clocked_out:
            message += f\"&bull; {name} at {fmt_time(out_time)} ({source})<br>\"
        message += (
            \"<br>Review or adjust these entries \"
            \"<a href='https://erp.craftedgoods.ca/app/employee-checkin/'>here</a>.\"
            \"<br><br>\"
        )

    if scheduled_no_show:
        message += \"<b>Scheduled today but no clock-IN:</b><br>\"
        for sh in scheduled_no_show:
            display = sh.get(\"prefered_name\") or sh.get(\"employee\")
            when = fmt_time(sh.get(\"time_in\"))
            outlet = sh.get(\"outlet_name\") or \"\"
            message += f\"&bull; {display} — scheduled {when} at {outlet}<br>\"
        message += \"<br>\"

    if missing_in_employees:
        message += \"<b>Employees with checkins today but missing a clock-IN row:</b><br>\"
        message += \"<br>\".join(missing_in_employees)
        message += (
            \"<br><a href='https://erp.craftedgoods.ca/app/employee-checkin/'>\"
            \"Fix missing entries here</a><br><br>\"
        )

    message += \"These are the clock entries for today:<br>\"
    message += complete_logs_table

    frappe.sendmail(
        recipients=RECIPIENT_EMAIL,
        sender=SENDER_EMAIL,
        subject=subject,
        message=message,
    )
except Exception:
    frappe.log_error(title='Check Entries for Today', message=frappe.get_traceback())
    raise
