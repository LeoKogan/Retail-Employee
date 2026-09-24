# Define current date and time
current_date = frappe.utils.today()  # Get today's date in YYYY-MM-DD format
current_datetime = frappe.utils.now()  # Get the current date and time in YYYY-MM-DD HH:MM:SS format
automatic_clock_outs = 0

# Define time intervals in minutes
shift_time_check_window = 120  # Time window (in minutes) to check for shifts that ended recently (widened for cron recovery)
clock_out_grace_period = 15    # Grace period (in minutes) after shift end for employees to clock out manually

# Calculate the start and end of the day to limit the range for checking employee clock-ins
day_start = frappe.utils.add_to_date(current_date, hours=0, minutes=0, seconds=0, as_datetime=True)
day_end = frappe.utils.add_to_date(current_date, hours=23, minutes=59, seconds=59, as_datetime=True)

# Calculate the lower time limit for fetching shifts that ended recently
shift_end_check_limit = frappe.utils.add_to_date(current_datetime, minutes=-shift_time_check_window)

# Fetch recent shifts from the 'CRAFTED Store Schedule' table
recent_shifts = frappe.db.get_all(
    'CRAFTED Store Schedule',
    filters=[['time_out', '>=', shift_end_check_limit], ['time_out', '<', current_datetime]],
    fields=['name', 'employee', 'time_in', 'time_out'],
    order_by='time_out'
)

# Fetch employee check-in entries from the 'Employee Checkin' table
today_checkins = frappe.db.get_all(
    'Employee Checkin',
    filters=[['time', '>=', day_start], ['time', '<=', day_end]],
    fields=['employee', 'log_type', 'time'],
    order_by='time'
)

# Process each shift to check for missing clock-out entries
for shift in recent_shifts:
    # Calculate the time limit by which the employee should have clocked out (grace period applied)
    grace_period_expiry = frappe.utils.add_to_date(shift['time_out'], minutes=clock_out_grace_period)

    # Filter clock entries for the current employee based on the shift employee ID
    employee_checkins = [entry for entry in today_checkins if entry['employee'] == shift['employee']]

    # Prefer auto-OUT only when there is an unpaired IN today (stack: IN pushes, OUT pops)
    unpaired_ins = 0
    for entry in employee_checkins:
        if entry['log_type'] == 'IN':
            unpaired_ins += 1
        elif entry['log_type'] == 'OUT' and unpaired_ins > 0:
            unpaired_ins -= 1

    try:
        frappe.log_error(
            "Minutes " + str(current_datetime).split(".")[0] + "> grace  " + str(grace_period_expiry)
        )
    except Exception:
        pass

    # Skip if no unpaired IN (already clocked out, or never clocked in)
    if unpaired_ins == 0:
        continue

    if str(current_datetime).split(".")[0] > str(grace_period_expiry):
        # Automatically create a clock-out entry for the employee
        auto_clock_out_entry = frappe.get_doc({
            'doctype': 'Employee Checkin',
            'employee': shift['employee'],
            'log_type': 'OUT',
            'time': shift['time_out'],
            'device_id': 'Automatic Clock Out'
        })
        # Insert + commit first so later mail/log failures cannot roll back the OUT
        auto_clock_out_entry.insert(ignore_permissions=True)
        frappe.db.commit()

        automatic_clock_outs = automatic_clock_outs + 1

        try:
            frappe.sendmail(
                recipients=['hr@craftedgoods.ca'],
                subject=f"Automatic Clock-Out for Employee {shift['employee']}",
                message=f"""
                <p>Employee <b>{shift['employee']}</b> was automatically clocked out.</p>
                <p><b>Shift End Time:</b> {frappe.utils.get_datetime_str(shift['time_out'])}</p>
                <p><b>Clock-Out Time:</b> {frappe.utils.get_datetime_str(auto_clock_out_entry.time)}</p>
                <p>This action was taken automatically after the grace period expired.</p>
            """
            )
        except Exception:
            pass

        try:
            frappe.log_error(
                title=f"Automatic Clock-Out for Employee {shift['employee']}",
                message=f"""
                <p>Employee <b>{shift['employee']}</b> was automatically clocked out.</p>
                <p><b>Shift End Time:</b> {frappe.utils.get_datetime_str(shift['time_out'])}</p>
                <p><b>Clock-Out Time:</b> {frappe.utils.get_datetime_str(auto_clock_out_entry.time)}</p>
                <p>This action was taken automatically after the grace period expired.</p>
            """
            )
        except Exception:
            pass
