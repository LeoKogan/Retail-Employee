frappe.ui.form.on('Timesheets', {
	refresh(frm) {
        // 1. Sort the child table array
        frm.doc.child_table_name.sort((a, b) => {
            let dateA = new Date(a.from_time);
            let dateB = new Date(b.from_time);
            return dateA - dateB;
        });

        // 2. Reset the row indices (idx) so the numbering is correct
        frm.doc.child_table_name.forEach((row, index) => {
            row.idx = index + 1;
        });

        // 3. Refresh the grid on the UI
        frm.refresh_field('Timesheet Detail');
    }
});