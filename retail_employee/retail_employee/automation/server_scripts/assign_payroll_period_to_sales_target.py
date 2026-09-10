# set payroll_period for sales_target_date
sales_target_date = doc.sales_target_date

Payroll_Period =  frappe.db.get_all('Payroll Period',
    filters={'start_date': ['<=', sales_target_date],'end_date':['>=', sales_target_date]},
    fields=['name'],
    pluck='name'
)
doc.payroll_period = Payroll_Period[0]