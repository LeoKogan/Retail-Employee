# After Submit on Timesheets.
# Same rebuild as "CRAFTED Sales Commissions Hourly Calculation", scoped to
# doc.payroll_period only. Does not look up the current Payroll Period.

Payroll_Period = doc.payroll_period

if Payroll_Period:
    Employee_Timesheets = frappe.db.get_all('Timesheets',
        filters={'payroll_period': ['=', Payroll_Period]},
        fields=['name'],
        pluck='name'
    )

    commissionable_amounts = frappe.get_all('Sales Targets',
        filters={'Payroll_Period': ['=', Payroll_Period]},
        fields=['commissionable_amount'],
        pluck='commissionable_amount'
    ) or []
    Total_Commissionable_Amount = round(sum(commissionable_amounts), 2)

    if Employee_Timesheets:
        Period_Worked_hours = round(sum(
            frappe.get_all('Timesheets Detail',
                fields=['hours'],
                filters=[['parent', 'in', Employee_Timesheets], ['role', '=', 'Sales Associate']],
                pluck='hours') or []
        ), 2)
    else:
        Period_Worked_hours = 0.00

    if Total_Commissionable_Amount > 0 and Period_Worked_hours:
        Commission_per_hour = round(Total_Commissionable_Amount / Period_Worked_hours, 2)
    else:
        Commission_per_hour = 0.00

    Employee_Sales = frappe.db.get_all('Sales By Employee',
        filters={'payroll_period': ['=', Payroll_Period]},
        fields=['date', 'employee', 'sales']
    )

    total_sales_by_employee = {}
    for record in Employee_Sales:
        employee = record['employee']
        sales = record['sales'] or 0
        if employee in total_sales_by_employee:
            total_sales_by_employee[employee] = total_sales_by_employee[employee] + sales
        else:
            total_sales_by_employee[employee] = sales

    Employee_Commissions_Detail = []
    for employee, total_sales in total_sales_by_employee.items():
        if frappe.db.exists('Timesheets', {'payroll_period': ['=', Payroll_Period], 'employee': ['=', employee]}):
            Employee_Timesheet = frappe.db.get_all('Timesheets',
                filters={'payroll_period': ['=', Payroll_Period], 'employee': ['=', employee]},
                fields=['name'],
                pluck='name'
            )[0]
            hour_rows = frappe.get_all('Timesheets Detail',
                fields=['hours'],
                filters=[['parent', '=', Employee_Timesheet], ['role', '=', 'Sales Associate']],
                pluck='hours') or []
            employee_worked_hours = round(sum(hour_rows), 2)

            if employee_worked_hours > 0:
                avg_sales_per_hour = round(total_sales / employee_worked_hours, 2)
            else:
                avg_sales_per_hour = 0

            Employee_Commissions_Detail.append({
                'employee': employee,
                'total_personal_sales': total_sales,
                'total_hours': employee_worked_hours,
                'average_sales_per_hour': avg_sales_per_hour
            })

    crafted_sales_commissions_name = frappe.db.exists('Sales Commissions', {'payroll_period': Payroll_Period})

    if crafted_sales_commissions_name:
        frappe.db.set_value('Sales Commissions', crafted_sales_commissions_name, {
            'total_worked_hours': Period_Worked_hours,
            'total_commissions': Total_Commissionable_Amount,
            'commission_per_hour': Commission_per_hour
        })
        crafted_sales_commissions = frappe.get_doc('Sales Commissions', crafted_sales_commissions_name)
    else:
        # Hourly script creates the period document when it is missing. Same here.
        crafted_sales_commissions = frappe.get_doc({
            'doctype': 'Sales Commissions',
            'payroll_period': Payroll_Period,
            'total_worked_hours': Period_Worked_hours,
            'total_commissions': Total_Commissionable_Amount,
            'commission_per_hour': Commission_per_hour
        })

    crafted_sales_commissions.set('employee_hours_commissions', [])

    for detail in Employee_Commissions_Detail:
        crafted_sales_commissions.append('employee_hours_commissions', {
            'employee': detail['employee'],
            'total_personal_sales': detail['total_personal_sales'],
            'total_hours': detail['total_hours'],
            'average_sales_per_hour': detail['average_sales_per_hour']
        })

    crafted_sales_commissions.save()
