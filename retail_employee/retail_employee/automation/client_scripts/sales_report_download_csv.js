frappe.ui.form.on('Sales Report', {
    refresh: function(frm) {
        frm.add_custom_button(__('Download CSV'), function() {
            // Define the columns for the main report
            let columns = [
                'Date', 'Sales Month', 'Sending Emails Completed', 
                'Total of Payments', 'Total of Consignor Sales', 
                'Effective Margin', 'Total GST'
            ];

            // Add child table columns
            let childColumns = [
                'Email', 'Name', 'Artisan %', 'Crafted %', 
                'Crafted Total Amount', 'Artisan Total Amount', 
                'Artisan Payment Method', 'Payment To Artisan', 
                'Total GST', 'Report Status'
            ];

            // Combine main columns and child table columns
            columns = columns.concat(childColumns);

            // Define the data rows for the main report fields
            let data = [
                [
                    frm.doc.date, 
                    frm.doc.month_of_sales, 
                    frm.doc.emails_sent, 
                    frm.doc.total_of_payments, 
                    frm.doc.total_of_consignor_sales, 
                    frm.doc.effective_margin, 
                    frm.doc.total_gst
                ]
            ];

            // Add child table data rows
            frm.doc.summary_of_sales_reports.forEach(row => {
                data.push([
                    '', '', '', '', '', '', '', // Placeholder for the main report data
                    row.email_id, 
                    row.consignor_name, 
                    row.artisan_percentage, 
                    row.crafted_percentage, 
                    row.crafted_total, 
                    row.artisan_total, 
                    row.artisan_payment_method,
                    row.payment_to_artisan, 
                    row.gst_total,
                    row.report_status
                ]);
            });

            // Convert data to CSV format
            let csvContent = \"data:text/csv;charset=utf-8,\" 
                + columns.join(\",\") + \"
\" 
                + data.map(e => e.join(\",\")).join(\"
\");

            // Create a download link and trigger the download
            let encodedUri = encodeURI(csvContent);
            let link = document.createElement(\"a\");
            link.setAttribute(\"href\", encodedUri);
            link.setAttribute(\"download\", frm.doc.name + \".csv\");
            document.body.appendChild(link); // Required for FF
            link.click();
            document.body.removeChild(link);
        });
    }
});
