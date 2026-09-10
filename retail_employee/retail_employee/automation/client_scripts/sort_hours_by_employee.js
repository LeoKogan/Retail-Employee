// Parent: Sales Commissions
const EHC_FIELD = 'employee_hours_commissions';

function crafted_avg_sales_per_hour(row) {
  const total_personal_sales = row.total_personal_sales || 0;
  const hours = row.total_hours || 0;
  return hours > 0 ? total_personal_sales / hours : 0;
}

function crafted_sort_employee_hours(frm) {
  const rows = frm.doc[EHC_FIELD] || [];
  const byEmployee = (a, b) => {
    const av = (a.employee || '').toString().toLowerCase();
    const bv = (b.employee || '').toString().toLowerCase();
    if (av < bv) return -1;
    if (av > bv) return 1;
    return 0;
  };

  const before = rows.map((r) => r.name).join('|');
  rows.sort(byEmployee);
  const after = rows.map((r) => r.name).join('|');
  if (before === after) {
    return false;
  }

  rows.forEach((r, i) => {
    r.idx = i + 1;
  });
  frm.refresh_field(EHC_FIELD);
  return true;
}

function crafted_set_row_average(row) {
  const avg = crafted_avg_sales_per_hour(row);
  if (row.average_sales_per_hour === avg) {
    return;
  }
  // Avoid set_value on refresh of unsaved/new rows without name
  if (row.name) {
    frappe.model.set_value(row.doctype, row.name, 'average_sales_per_hour', avg);
  } else {
    row.average_sales_per_hour = avg;
  }
}

function crafted_set_all_averages(frm) {
  (frm.doc[EHC_FIELD] || []).forEach((row) => crafted_set_row_average(row));
}

frappe.ui.form.on('Sales Commissions', {
  refresh(frm) {
    try {
      // Sort display order only when needed (does not mark form dirty by itself)
      crafted_sort_employee_hours(frm);
      // Fill missing averages for display; set_value only when value actually changes
      crafted_set_all_averages(frm);
    } catch (e) {
      console.error('Sort Hours by Employee (refresh)', e);
      frappe.msgprint({
        title: __('Sort Hours by Employee'),
        indicator: 'red',
        message: __('Client script error: {0}', [e.message || e]),
      });
    }
  },
});

frappe.ui.form.on('Employee Commissions Details', {
  total_hours(frm, cdt, cdn) {
    try {
      crafted_set_row_average(locals[cdt][cdn]);
    } catch (e) {
      console.error('Sort Hours by Employee (total_hours)', e);
      frappe.msgprint({
        title: __('Sort Hours by Employee'),
        indicator: 'red',
        message: __('Client script error: {0}', [e.message || e]),
      });
    }
  },
  total_personal_sales(frm, cdt, cdn) {
    try {
      crafted_set_row_average(locals[cdt][cdn]);
    } catch (e) {
      console.error('Sort Hours by Employee (total_personal_sales)', e);
      frappe.msgprint({
        title: __('Sort Hours by Employee'),
        indicator: 'red',
        message: __('Client script error: {0}', [e.message || e]),
      });
    }
  },
});
