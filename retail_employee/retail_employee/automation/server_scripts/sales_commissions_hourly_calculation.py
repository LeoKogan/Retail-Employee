today = frappe.utils.today()

# Get the start and end of today
start_of_day = frappe.utils.add_to_date(today, hours=0, minutes=0, seconds=0, as_datetime=True)
end_of_day = frappe.utils.add_to_date(today, hours=23, minutes=59, seconds=59, as_datetime=True)

Employee_Info = frappe.db.get_all('Employee Info', 
    filters={'employee_status':['=', \"Active\"]},
    fields=['employee','employee_status','prefered_name']
)

Payroll_Period = frappe.get_all('Payroll Period', 
    filters={'start_date': ['<=', today],'end_date':['>=', today]},
    fields=['name'],
    pluck='name')[0]

Employee_Timesheets = frappe.db.get_all('Timesheets', 
    filters={'payroll_period':['=', Payroll_Period]},
    fields=['name'],
    pluck='name'
)

Total_Commissionable_Amount = round(sum(frappe.get_all('Sales Targets', 
    filters={'Payroll_Period': ['=', Payroll_Period]},
    fields=[\"commissionable_amount\"],
    pluck='commissionable_amount'
)), 2)
    
Period_Worked_hours = round(sum(
    frappe.get_all(\"Timesheet Detail\", 
        fields=[\"hours\"], 
        filters=[[\"parent\", \"in\", Employee_Timesheets],['role','=','Sales Associate']],
        pluck='hours')
), 2)
    
if Total_Commissionable_Amount > 0:
    Commission_per_hour = round(Total_Commissionable_Amount/Period_Worked_hours, 2)
else:
    Commission_per_hour = 0.00

CRAFTED_Sales_Commissions = frappe.db.get_all('Sales Commissions',
    filters={'payroll_period':['=', Payroll_Period]},
    fields=['*']
)

Employee_Sales = frappe.db.get_all('Sales By Employee',
    filters={'payroll_period':['=', Payroll_Period]},
    fields=['date','employee','sales']
)

# Create a dictionary to hold the sum of sales for each employee
total_sales_by_employee = {}

# Iterate through each record in Employee_Sales
for record in Employee_Sales:
    employee = record['employee']
    sales = record['sales']
    if employee in total_sales_by_employee:
        total_sales_by_employee[employee] = total_sales_by_employee[employee] + sales
    else:
        total_sales_by_employee[employee] = sales

# Prepare the child table entries
Employee_Commissions_Detail = []
for employee, total_sales in total_sales_by_employee.items():
    if (frappe.db.exists('Timesheets', {'payroll_period':['=', Payroll_Period],'employee':['=', employee]})):
        Employee_Timesheet = frappe.db.get_all('Timesheets', 
            filters={'payroll_period':['=', Payroll_Period],'employee':['=', employee]},
            fields=['name'],
            pluck='name'
        )[0]
        employee_worked_hours = round(sum(frappe.get_all(\"Timesheet Detail\", 
            fields=[\"hours\"], 
            filters=[[\"parent\", \"=\", Employee_Timesheet],['role','=','Sales Associate']],
            pluck='hours')), 2)
        
        # Calculate average sales per hour
        if employee_worked_hours > 0:
            avg_sales_per_hour = round(total_sales / employee_worked_hours, 2)
        else:
            avg_sales_per_hour = 0
            
        Employee_Commissions_Detail.append(frappe.get_doc({
            'doctype': 'Employee Commissions Details', 
            'employee': employee,
            'total_personal_sales': total_sales,
            'total_hours': employee_worked_hours,
            'average_sales_per_hour': avg_sales_per_hour  # ADD THIS LINE
        }))
    
# Check if the Sales Commissions document exists for the payroll period
crafted_sales_commissions_name = frappe.db.exists('Sales Commissions', {'payroll_period': Payroll_Period})

if crafted_sales_commissions_name:
    # Update the main fields on the existing Document
    frappe.db.set_value('Sales Commissions', crafted_sales_commissions_name, {
        'total_worked_hours': Period_Worked_hours,
        'total_commissions': Total_Commissionable_Amount,
        'commission_per_hour': Commission_per_hour
    })
    # Fetch it so we can update the child table entries as well
    crafted_sales_commissions = frappe.get_doc('Sales Commissions', crafted_sales_commissions_name)
else:
    # Document does not exist, create a new one
    crafted_sales_commissions = frappe.get_doc({
        'doctype': 'Sales Commissions',
        'payroll_period': Payroll_Period,
        'total_worked_hours': Period_Worked_hours,
        'total_commissions': Total_Commissionable_Amount,
        'commission_per_hour': Commission_per_hour
    })

# Clear existing child table entries to prevent duplicates
crafted_sales_commissions.set('employee_hours_commissions', [])

# Append new child table entries
for detail in Employee_Commissions_Detail:
    # Calculate average sales per hour again for the append
    if detail.total_hours > 0:
        avg_sales = round(detail.total_personal_sales / detail.total_hours, 2)
    else:
        avg_sales = 0
        
    crafted_sales_commissions.append('employee_hours_commissions', {
        'employee': detail.employee,
        'total_personal_sales': detail.total_personal_sales,
        'total_hours': detail.total_hours,
        'average_sales_per_hour': avg_sales  # ADD THIS LINE
    })

# Save or insert the document
crafted_sales_commissions.save()
frappe.db.commit()  # Ensure changes are committed to the database