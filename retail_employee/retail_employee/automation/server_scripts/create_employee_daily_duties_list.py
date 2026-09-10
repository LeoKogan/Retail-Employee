# Get today's date range
today = frappe.utils.today()
today_start = frappe.utils.get_datetime(f\"{today} 00:00:00\")
today_end = frappe.utils.get_datetime(f\"{today} 23:59:59\")
 
# Get day of week (Monday=0, Sunday=6)
day_of_week = frappe.utils.get_datetime(today).weekday()
day_names = [\"Monday\", \"Tuesday\", \"Wednesday\", \"Thursday\", \"Friday\", \"Saturday\", \"Sunday\"]
today_name = day_names[day_of_week]

# Log day info
print(f\"Create Employee Daily Duties - Day: {today_name} ({day_of_week})\")

# Get all schedules for today
schedules = frappe.get_all(
    \"Store Schedule\",
    fields=[\"name\", \"outlet_name\", \"time_in\", \"time_out\", \"employee_email\"],
    filters={
        \"time_in\": [\"between\", [today_start, today_end]]
    }
)

# Get all outlets (excluding child table fields)
outlets = frappe.get_all(
    \"Outlets\",
    fields=[\"name\", \"branch\", \"outlet_name\"]
)

# Create a mapping of outlet_name to outlet name (for quick lookup)
outlet_map = {outlet.outlet_name: outlet.name for outlet in outlets}

# Track statistics
todos_created = 0
errors_encountered = 0

# Process each scheduled employee
for schedule in schedules:
    outlet_name = schedule.outlet_name
    employee_email = schedule.employee_email
    time_in = schedule.time_in
    time_out = schedule.time_out
    
    if outlet_name not in outlet_map:
        frappe.log_error(
            f\"Outlet '{outlet_name}' not found in Outlets doctype\",
            \"Todo Creation Error\"
        )
        errors_encountered = errors_encountered + 1
        continue
    
    # Get the outlet document to access child table
    outlet_doc = frappe.get_doc(\"Outlets\", outlet_map[outlet_name])
    
    # Determine which shift categories apply based on time_in and time_out
    applicable_categories = []
    
    # Extract hours for comparison
    time_in_hour = time_in.hour
    time_out_hour = time_out.hour
    
    # Opening shift: time_in before 12pm (noon)
    if time_in_hour < 12:
        applicable_categories.append(\"Opening\")
    
    # Mid-shift: time_in between 9am-2pm OR time_out after 1pm
    if (9 <= time_in_hour < 14) or (time_out_hour >= 13):
        applicable_categories.append(\"Mid-shift\")
    
    # Closing shift: time_out after 4pm (16:00)
    if time_out_hour >= 16:
        applicable_categories.append(\"Closing\")
    
    # Extra category always applies to everyone
    applicable_categories.append(\"Extra\")
    
    # Log shift assignment to console
    print(f\"Shift Assignment - Employee: {employee_email}, Time: {time_in_hour}:00-{time_out_hour}:00, Categories: {applicable_categories}\")
    
    # Filter and organize duties by category
    # Group duties by category, combining Everyday and specific day tasks
    duties_by_category = {}
    
    for duty in outlet_doc.outlet_duties:
        # Check if duty matches today or everyday AND is in applicable categories
        if duty.dayoftheweek in [today_name, \"Everyday\"] and duty.category in applicable_categories:
            if duty.category not in duties_by_category:
                duties_by_category[duty.category] = []
            duties_by_category[duty.category].append(duty)
    
    # Process each category with continuous numbering
    for category in applicable_categories:
        if category not in duties_by_category:
            continue
        
        task_number = 1
        
        # Process all duties in this category (both Everyday and specific day)
        for duty in duties_by_category[category]:
            # Split employee_duties by newlines to create separate tasks
            duty_lines = duty.employee_duties.split('
') if duty.employee_duties else []
            
            for duty_line in duty_lines:
                # Skip empty lines
                duty_line = duty_line.strip()
                if not duty_line:
                    continue
                
                # Add task number prefix
                numbered_duty = f\"{task_number}- {duty_line}\"
                
                # Increment task number for next task in this category
                task_number = task_number + 1
                    
                try:
                    # Check if todo already exists to avoid duplicates
                    existing_todo = frappe.db.exists(
                        \"ToDo\",
                        {
                            \"allocated_to\": employee_email,
                            \"reference_type\": \"Store Schedule\",
                            \"reference_name\": schedule.name,
                            \"description\": numbered_duty,
                            \"custom_category\": category
                        }
                    )
                    
                    if not existing_todo:
                        todo = frappe.get_doc({
                            \"doctype\": \"ToDo\",
                            \"allocated_to\": employee_email,
                            \"description\": numbered_duty,
                            \"reference_type\": \"Store Schedule\",
                            \"reference_name\": schedule.name,
                            \"priority\": \"Medium\",
                            \"status\": \"Open\",
                            \"date\": today,
                            \"custom_category\": category
                        })
                        todo.insert(ignore_permissions=True)
                        todos_created = todos_created + 1
                        
                except Exception as e:
                    frappe.log_error(
                        f\"Error creating todo for {employee_email}: {str(e)}\",
                        \"Todo Creation Error\"
                    )
                    errors_encountered = errors_encountered + 1

# Commit all changes
frappe.db.commit()

# Create summary message
summary_message = f\"Daily Duties Created: {todos_created} todos for {len(schedules)} employees on {today_name}, {today}\"
if errors_encountered > 0:
    summary_message = summary_message + f\"
⚠️ {errors_encountered} errors encountered (check Error Log)\"

# Print summary to console logs
print(summary_message)

# Send notification to Leo
try:
    notification = frappe.get_doc({
        \"doctype\": \"Notification Log\",
        \"subject\": f\"Daily Duties Created - {today}\",
        \"email_content\": summary_message,
        \"for_user\": \"leo@craftedgoods.ca\",
        \"type\": \"Alert\",
        \"document_type\": \"Store Schedule\",
        \"read\": 0
    })
    notification.insert(ignore_permissions=True)
    frappe.db.commit()
except Exception as e:
    frappe.log_error(
        f\"Error sending notification to Leo: {str(e)}\",
        \"Notification Error\"
    )