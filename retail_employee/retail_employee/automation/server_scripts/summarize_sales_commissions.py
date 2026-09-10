total_of_payments=0.00
total_of_consignor_sales=0.00
effective_margin=0.00
total_gst=0.00

for rows in doc.summary_of_sales_reports:
    total_of_consignor_sales    = total_of_consignor_sales  + rows.crafted_total 
    total_of_payments           = total_of_payments         + rows.payment_to_artisan
    total_gst                   = total_gst                 + rows.gst_total
    

doc.total_of_payments=total_of_payments
doc.total_of_consignor_sales=total_of_consignor_sales
doc.effective_margin= 100 - ( total_of_payments / total_of_consignor_sales * 100)
doc.total_gst=total_gst