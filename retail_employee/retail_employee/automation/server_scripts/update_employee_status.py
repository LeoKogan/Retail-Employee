crafted_employee_info = frappe.db.get_value('Employee Info', {'employee': doc.employee}, 'name')
if crafted_employee_info:
    # Load the existing record using its name
    crafted_info_doc = frappe.get_doc('Employee Info', crafted_employee_info)
    
    # Update the fields with the information from the Employee doc
    crafted_info_doc.status = doc.status
    
    # Save the updated document
    crafted_info_doc.save(ignore_permissions=True)