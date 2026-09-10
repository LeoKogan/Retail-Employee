try:
    # Initialize total payable amounts for personal and team commissions
    total_personal_commission_payable = 0
    total_team_commission_payable = 0

    # Calculate the total hours worked by summing up the hours of all employees
    total_hours_worked = sum((employee.total_hours or 0) for employee in (doc.employee_hours_commissions or []))

    # Calculate commission earned per hour (guard empty / zero hours)
    if total_hours_worked:
        doc.commission_per_hour = (doc.total_commissions or 0) / total_hours_worked
    else:
        doc.commission_per_hour = 0

    # Loop through each employee's record to calculate individual commissions
    for employee in (doc.employee_hours_commissions or []):
        # Personal commission from personal sales and rate
        employee.total_personal_commission = (employee.total_personal_sales or 0) * (employee.personal_commission_rate or 0) / 100
        total_personal_commission_payable = total_personal_commission_payable + employee.total_personal_commission

        # Store/team share from hour-weighted pool and store rate
        employee.total_store_commission = doc.commission_per_hour * (employee.total_hours or 0) * (employee.store_commission_rate or 0) / 100
        total_team_commission_payable = total_team_commission_payable + employee.total_store_commission

    # Parent totals (fieldnames must match Sales Commissions)
    doc.total_payable_personal_comm = total_personal_commission_payable
    doc.total_payable_team_comm = total_team_commission_payable
    doc.total_worked_hours = round(total_hours_worked, 2)

    # Estimate total payable cost including hourly wage (assuming $18 per hour)
    doc.estimated_total_payable_cost = total_hours_worked * 18 + total_team_commission_payable + total_personal_commission_payable
except Exception:
    frappe.log_error(
        title=\"Calculate Employee Commissions Details\",
        message=frappe.get_traceback()
        + \"

Doc: \"
        + str(getattr(doc, \"name\", None))
        + \"
total_commissions=\"
        + str(getattr(doc, \"total_commissions\", None))
        + \"
rows=\"
        + str(len(doc.employee_hours_commissions or [])),
    )
    raise
