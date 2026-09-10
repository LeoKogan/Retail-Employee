# set property
if doc.actual_sales is None:
    doc.actual_sales=  0.00
if doc.actual_sales > doc.sales_target:
	doc.commissionable_amount =  doc.actual_sales - doc.sales_target
else:
    doc.commissionable_amount =  0.00