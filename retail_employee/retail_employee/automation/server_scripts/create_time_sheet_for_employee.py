# Set debug log level
# Function to log detailed error
shift_outlet_name = \"Events Outside Crafted\"
shift_role = \"Event Worker\"
shift_id = \"\"
Notes=\"\"
shift_time_in= \"\"
shift_time_out= \"\"
Scheduled_hours= 0

def log_error_with_context(e, context):
    error_message = f\"Error in context: {context} - Exception: {str(e)}\"
    frappe.log_error(error_message)
#Available Fields on Employee Checkin
#  Clock_out.employee
#  Clock_out.employee_name
#  Clock_out.log_type
#  Clock_out.shift
#  Clock_out.time
#  Clock_out.device_id
#  Clock_out.skip_auto_attendance
#  Clock_out.attendance
#  Clock_out.shift_start
#  Clock_out.shift_end
#  Clock_out.shift_actual_start
#  Clock_out.shift_actual_end
Clock_out=doc
try:
    employee_ID=Clock_out.employee
    if Clock_out.log_type == \"OUT\":
        time_clock_out = Clock_out.time
        #get Current Payroll
        Payroll_Period =  frappe.db.get_all('Payroll Period',
            filters={'start_date': ['<=', time_clock_out],'end_date':['>=', time_clock_out]},
            fields=['name'],
            pluck='name'
        )[0]
        
        #get the Checkin
        Clock_in =  frappe.db.get_all('Employee Checkin',
            filters={'time': ['<', time_clock_out],'log_type':['=', 'IN'],'employee':['=', employee_ID]},
            fields=['*'],
            order_by='time desc'
        )[0]
        
        today = frappe.utils.today()
        # Get the start and end of today
        start_of_day = frappe.utils.add_to_date(today, hours=0, minutes=0, seconds=0, as_datetime=True)
        end_of_day =   frappe.utils.add_to_date(today, hours=23, minutes=59, seconds=59, as_datetime=True)
        #Check for Holidays
        Today_is_a_holiday = frappe.db.exists({\"doctype\":\"Holiday\",\"holiday_date\":[\"=\",today]})
        #Make an effort to get a scheduled shift
        scheduled_shift =  frappe.db.get_all(\"Store Schedule\",
            filters={'time_in': ['>', start_of_day],'time_out': ['<', end_of_day],'employee':['=', employee_ID]},
            fields=['name','outlet_name','time_in','time_out','role']
        )
        #If there is a shift pull relevant data
        if bool(scheduled_shift):
            shift_outlet_name = scheduled_shift[0].outlet_name
            shift_role = scheduled_shift[0].role
            shift_id = scheduled_shift[0].name
            shift_time_in=scheduled_shift[0].time_in
            shift_time_out=scheduled_shift[0].time_out
            Scheduled_hours = frappe.utils.time_diff_in_hours(shift_time_out,shift_time_in)
        #Check if exist or Create Timesheet for the pyaroll period 
        Employee_Timesheet = frappe.db.get_all('Timesheets',
            filters={'payroll_period':['=', Payroll_Period],'employee':['=', employee_ID]},
            fields=['*']
        )
        Worked_hours= frappe.utils.time_diff_in_hours(Clock_out.time,Clock_in.time)
        
        #If Employee_Timesheet doesn't exist for the period we create one and add the timelog entry for today
        
        if Clock_in.device_id is not None:
            Notes = Notes + \"Clock In at:
\" + Clock_in.device_id+ \"
\"
        if Clock_out.device_id is not None:
            Notes = Notes +\"Clock Out at:
\" + Clock_out.device_id+ \"
\"
        time_log={'outlet_name': shift_outlet_name,
                'role': shift_role,
                'id':shift_id,
                'from_time':Clock_in.time,
                'to_time':Clock_out.time,
                'hours': Worked_hours,
                'extra_hrs' : 0.0,
                'expected_hours': Scheduled_hours,
                'notes': Notes}
        #if is a Holiday We need to pay 1.5 per worked hour
        if Today_is_a_holiday is not None:
            time_log[\"extra_hrs\"] = (Worked_hours * 0.5)
            time_log[\"notes\"]= Notes + \"This is a holiday, extra hours have been added to extra hours\"+ \"
\"

        if bool(Employee_Timesheet):
            #If Employee_Timesheet exist for the period we need to read the timelog entries to determine if this is an update or a new one
            Existing_Employee_Timesheet = frappe.get_doc('Timesheets',Employee_Timesheet[0].name)
            #once Timesheet check if this is a modification update Timeshet detail
            for timelog_entry in Existing_Employee_Timesheet.time_logs:
                if timelog_entry.notes == \"Daily Clock Hours Calculation\":
                    Existing_Employee_Timesheet.remove(timelog_entry)
            Existing_Employee_Timesheet.append(\"time_logs\", time_log)
            Existing_Employee_Timesheet.save()
        else:
            Employee_Timesheet =  frappe.get_doc(dict(
                    doctype = 'Timesheets',
                    employee = employee_ID,
                    payroll_period = Payroll_Period
                ))
            Employee_Timesheet.append(\"time_logs\", time_log)
            Employee_Timesheet.insert()

except Exception as e:
     log_error_with_context(e, \"Error Overall Script\")
     frappe.log_error(frappe.get_traceback(), \"Create Time Sheet for Employee Script. Failed\")