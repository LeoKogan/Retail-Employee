shift_outlet_name = \"Events Outside Crafted\"
shift_role = \"Event Worker\"
shift_id = \"\"
Notes=\"\"
today = frappe.utils.today()
# Get the start and end of today
start_of_day = frappe.utils.add_to_date(today, hours=0, minutes=0, seconds=0, as_datetime=True)
end_of_day =   frappe.utils.add_to_date(today, hours=23, minutes=59, seconds=59, as_datetime=True)

Clock_Entries = frappe.db.get_all('Employee Checkin',
    filters={\"time\": [\"between\", [start_of_day, end_of_day]],'log_type': ['=', 'IN']},
    fields=['employee','employee_name','log_type','time','device_id'],
    order_by='time')

Payroll_Period =  frappe.db.get_all('Payroll Period',
    filters={'start_date': ['<=', today],'end_date':['>=', today]},
    fields=['name'],
    pluck='name'
    )[0]


for entry in Clock_Entries:
    employee_ID =  entry['employee']
    #frappe.log_error(\"employee_ID: \"+ employee_ID + \" Clock \"+str(entry['log_type'])+\" at \" + str(entry['time']))
    Employee_Timesheet = frappe.db.get_all('Timesheets',
        filters={'payroll_period':['=', Payroll_Period],'employee':['=', employee_ID]},
        fields=['*']
    )
    scheduled_shift =  frappe.db.get_all(\"Store Schedule\",
        filters={'time_in': ['>', start_of_day],'time_out': ['<', end_of_day],'employee':['=', employee_ID]},
        fields=['name','outlet_name','time_in','time_out','role']
    )

    #If there is a shift pull relevant data
    if bool(scheduled_shift):
        #frappe.log_error(\"From: \"+str(scheduled_shift[0].time_in) +\" | to: \"+ str(scheduled_shift[0].time_out))
        shift_outlet_name = scheduled_shift[0].outlet_name
        shift_role = scheduled_shift[0].role
        shift_id = scheduled_shift[0].name
        shift_time_in=scheduled_shift[0].time_in
        shift_time_out=scheduled_shift[0].time_out
        #frappe.log_error(\"shift_time_in: \"+str(shift_time_in))
        #frappe.log_error(\"shift_time_out: \"+str(shift_time_out))
        # Get the current time as a datetime object
        time_now =  frappe.utils.now()
        hours_from_clock_in = round(frappe.utils.time_diff_in_hours(time_now,entry['time']),2)
        Scheduled_hours= frappe.utils.time_diff_in_hours(shift_time_out,shift_time_in)
        #frappe.log_error(\"hours_from_clock_in: \"+str(hours_from_clock_in))
        #frappe.log_error(\"Scheduled_hours: \" +str(Scheduled_hours))
        if hours_from_clock_in  < Scheduled_hours:
            time_log={
                'outlet_name': shift_outlet_name,
                'role': shift_role,
                'id':shift_id,
                'from_time': entry['time'],
                'to_time':time_now,
                'hours':hours_from_clock_in  ,
                'extra_hrs' : 0.0,
                'expected_hours': Scheduled_hours,
                'notes': \"Daily Clock Hours Calculation\"
            }
            
            if bool(Employee_Timesheet):
                #If Employee_Timesheet exist for the period we need to read the timelog entries to determine if this is an update or a new one
                Existing_Employee_Timesheet = frappe.get_doc('Timesheets',Employee_Timesheet[0].name)
                #once Timesheet check if this is a modification update Timeshet detail
                found_and_updated = False
                for timelog in Existing_Employee_Timesheet.time_logs:
                    if timelog.from_time == time_log['from_time']:
                        # Update the existing entry with new data from time_log
                        timelog.to_time = time_now
                        timelog.hours = hours_from_clock_in
                        found_and_updated = True
                        break 
                # If no existing entry was found and updated, append the new time_log
                #frappe.log_error(\"Lo encontre?: \" +str(found_and_updated))
                if not found_and_updated:
                    Existing_Employee_Timesheet.append(\"time_logs\", time_log)
                    # Save the changes to the timesheet
                Existing_Employee_Timesheet.save()
            else:
                Employee_Timesheet =  frappe.get_doc(dict(
                    doctype = 'Timesheets',
                    employee = employee_ID,
                    payroll_period = Payroll_Period
                ))
                Employee_Timesheet.append(\"time_logs\", time_log)
                Employee_Timesheet.insert()
    