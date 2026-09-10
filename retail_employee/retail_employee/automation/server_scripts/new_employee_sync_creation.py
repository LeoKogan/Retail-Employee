frappe.get_doc(dict(
    doctype = 'Employee Info',
	employee = doc.employee,
    personal_commission_rate=\"0.1\",
    crafted_commission_rate=\"0.1\",
    prefered_name = doc.first_name
)).insert()