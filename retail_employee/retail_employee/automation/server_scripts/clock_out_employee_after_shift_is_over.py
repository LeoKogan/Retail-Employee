# Define current date and time
current_date = frappe.utils.today()  # Get today's date in YYYY-MM-DD format
current_datetime = frappe.utils.now()  # Get the current date and time in YYYY-MM-DD HH:MM:SS format
automatic_clock_outs=0 

# Define time intervals in minutes
shift_time_check_window = 40   # Time window (in minutes) to check for shifts that ended recently
clock_out_grace_period = 15    # Grace period (in minutes) after shift end for employees to clock out manually

# Calculate the start and end of the day to limit the range for checking employee clock-ins
day_start = frappe.utils.add_to_date(current_date, hours=0, minutes=0, seconds=0, as_datetime=True)
day_end = frappe.utils.add_to_date(current_date, hours=23, minutes=59, seconds=59, as_datetime=True)

# Calculate the lower time limit for fetching shifts that ended recently
shift_end_check_limit = frappe.utils.add_to_date(current_datetime, minutes=-shift_time_check_window)

# Fetch recent shifts from the 'Store Schedule' table
recent_shifts = frappe.db.get_all(
    'Store Schedule',
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
    
    # Check for any clock-out entries ('OUT') for the employee for this shift
    clock_out_entries = [entry for entry in employee_checkins if entry['log_type'] == 'OUT']
    frappe.log_error(\"Minutes \"+ str(current_datetime).split(\".\")[0]+ \"> grace  \" + str(grace_period_expiry))
    
    # If no clock-out entry exists and the current time is past the grace period expiry
    if not clock_out_entries and str(current_datetime).split(\".\")[0] > str(grace_period_expiry):
        # Automatically create a clock-out entry for the employee
        auto_clock_out_entry = frappe.get_doc({
            'doctype': 'Employee Checkin',            # Specify the document type as 'Employee Checkin'
            'employee': shift['employee'],            # Assign the employee ID from the shift
            'log_type': 'OUT',                        # Set log type to 'OUT' to indicate a clock-out
            'time': shift['time_out'],                # Use the shift's time_out as the clock-out time
            'device_id': 'Automatic Clock Out'        # Indicate this is an automated clock-out
        })
        # Insert the document into the database, bypassing permission checks
        auto_clock_out_entry.insert(ignore_permissions=True)
        
        # Increment the count of automatic clock-out entries
        automatic_clock_outs = automatic_clock_outs  + 1
        
        # Send an email notification for this automatic clock-out
        sendmail(
            recipients=['hr@craftedgoods.ca'],  # Replace with the recipient's email address
            subject=f\"Automatic Clock-Out for Employee {shift['employee']}\",
            message=f\"\"\"
                <p>Employee <b>{shift['employee']}</b> was automatically clocked out.</p>
                <p><b>Shift End Time:</b> {get_datetime_str(shift['time_out'])}</p>
                <p><b>Clock-Out Time:</b> {get_datetime_str(auto_clock_out_entry.time)}</p>
                <p>This action was taken automatically after the grace period expired.</p>
            \"\"\"
        )
        frappe.log_error(
        title=f\"Automatic Clock-Out for Employee {shift['employee']}\",
        message=f\"\"\"
                <p>Employee <b>{shift['employee']}</b> was automatically clocked out.</p>
                <p><b>Shift End Time:</b> {get_datetime_str(shift['time_out'])}</p>
                <p><b>Clock-Out Time:</b> {get_datetime_str(auto_clock_out_entry.time)}</p>
                <p>This action was taken automatically after the grace period expired.</p>
            \"\"\"
        )