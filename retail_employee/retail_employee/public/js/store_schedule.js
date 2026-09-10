frappe.ui.form.on('Store Schedule', {
  setup(frm) {
    frm.set_query('employee', () => ({
      filters: [['Employee Info', 'employee_status', '=', 'Active']],
    }));
  },

  refresh(frm) {
    try {
      if (!frm.doc.time_in) {
        frm.set_value('time_in', frappe.datetime.get_today() + ' 09:00:00');
      }
      // Default role only on new docs — do not overwrite on every refresh
      if (frm.is_new() && !frm.doc.role) {
        frm.set_value('role', 'Sales Associate');
      }
      crafted_schedule_apply_color(frm);
      crafted_schedule_refresh_publish_buttons(frm);
    } catch (e) {
      console.error('Store Schedule-Form (refresh)', e);
      frappe.msgprint({
        title: __('Store Schedule'),
        indicator: 'red',
        message: __('Client script error: {0}', [e.message || e]),
      });
    }
  },

  validate(frm) {
    try {
      const name = crafted_schedule_pref_name(frm);
      const hasName = !!name;
      crafted_schedule_set_if_changed(frm, 'assigned', hasName ? 1 : 0);

      const outlet = (frm.doc.outlet_name || '').trim();
      const dur = crafted_schedule_duration_label(frm);
      let cal = hasName
        ? (name + ' @ ' + outlet).trim()
        : ('Open Shift @ ' + outlet).trim();
      if (dur) {
        cal = cal + ' · ' + dur;
      }
      crafted_schedule_set_if_changed(frm, 'calendar_text', cal);

      crafted_schedule_apply_color(frm);

      if (frm.doc.time_in && frm.doc.time_out) {
        const inDay = String(frm.doc.time_in).slice(0, 10);
        const outDay = String(frm.doc.time_out).slice(0, 10);
        if (inDay !== outDay) {
          frappe.msgprint(__('Time In and Time Out must be on the same day.'));
          frappe.validated = false;
          return;
        }
        const timeInDate = frappe.datetime.str_to_obj(frm.doc.time_in);
        const timeOutDate = frappe.datetime.str_to_obj(frm.doc.time_out);
        if (!timeInDate || !timeOutDate) {
          frappe.msgprint(__('Invalid Time In or Time Out.'));
          frappe.validated = false;
          return;
        }
        const diffInHours = (timeOutDate - timeInDate) / (1000 * 60 * 60);
        if (diffInHours < 0) {
          frappe.msgprint(__('Time Out must be after Time In.'));
          frappe.validated = false;
          return;
        }
        if (diffInHours === 0) {
          frappe.msgprint(__('Time Out must be after Time In.'));
          frappe.validated = false;
          return;
        }
        crafted_schedule_set_if_changed(
          frm,
          'expected_work_hours',
          Number(diffInHours.toFixed(2))
        );
      }
    } catch (e) {
      console.error('Store Schedule-Form (validate)', e);
      frappe.msgprint({
        title: __('Store Schedule'),
        indicator: 'red',
        message: __('Client script error: {0}', [e.message || e]),
      });
      frappe.validated = false;
    }
  },

  outlet_name(frm) {
    try {
      if (!frm.doc.outlet_name) {
        crafted_schedule_set_if_changed(frm, 'outlet_color', '');
        crafted_schedule_apply_color(frm);
        return;
      }
      frappe.db.get_value('Outlets', frm.doc.outlet_name, 'outlet_color').then((r) => {
        const c = (r && r.message && r.message.outlet_color) || '';
        crafted_schedule_set_if_changed(frm, 'outlet_color', c);
        crafted_schedule_apply_color(frm);
      });
    } catch (e) {
      console.error('Store Schedule-Form (outlet_name)', e);
    }
  },

  prefered_name(frm) {
    crafted_schedule_apply_color(frm);
  },

  time_in(frm) {
    try {
      if (!frm.doc.time_out && frm.doc.time_in) {
        const day = String(frm.doc.time_in).slice(0, 10);
        frm.set_value('time_out', day + ' 17:00:00');
      }
      if (frm.fields_dict.time_out && frm.fields_dict.time_out.datepicker) {
        frm.fields_dict.time_out.datepicker.update({
          minDate: frm.doc.time_in ? frappe.datetime.str_to_obj(frm.doc.time_in) : null,
        });
      }
    } catch (e) {
      console.error('Store Schedule-Form (time_in)', e);
    }
  },

  time_out(frm) {
    try {
      if (frm.fields_dict.time_in && frm.fields_dict.time_in.datepicker) {
        frm.fields_dict.time_in.datepicker.update({
          maxDate: frm.doc.time_out ? frappe.datetime.str_to_obj(frm.doc.time_out) : null,
        });
      }
    } catch (e) {
      console.error('Store Schedule-Form (time_out)', e);
    }
  },
});

/** Soft Outlets.outlet_color is for UI tints; calendar needs darker fills. */
const CRAFTED_OUTLET_CALENDAR_COLORS = {
  'CFM West': '#9fb072',
  'CFM South': '#5a82b3',
  'Events Outside Crafted': '#9b7bb8',
  Wharehouse: '#d4a574',
};


function crafted_schedule_time_hm(dt) {
  if (!dt) return '';
  const s = String(dt);
  // \"YYYY-MM-DD HH:MM:SS\" or ISO
  const m = s.match(/(\d{2}):(\d{2})/);
  return m ? m[1] + ':' + m[2] : '';
}

function crafted_schedule_duration_label(frm) {
  if (!frm.doc.time_in || !frm.doc.time_out) return '';
  const a = frappe.datetime.str_to_obj(frm.doc.time_in);
  const b = frappe.datetime.str_to_obj(frm.doc.time_out);
  if (!a || !b) return '';
  const hrs = (b - a) / (1000 * 60 * 60);
  if (!(hrs > 0)) return '';
  const start = crafted_schedule_time_hm(frm.doc.time_in);
  const end = crafted_schedule_time_hm(frm.doc.time_out);
  const hs = Number.isInteger(hrs) ? String(hrs) : hrs.toFixed(1);
  return start + ' - ' + end + ' (' + hs + ' hs)';
}

function crafted_schedule_pref_name(frm) {
  return (frm.doc.prefered_name && String(frm.doc.prefered_name).trim()) || '';
}

function crafted_schedule_set_if_changed(frm, field, value) {
  const cur = frm.doc[field];
  if (cur === value) return;
  // Avoid noisy dirty when both are empty-ish
  if ((cur == null || cur === '') && (value == null || value === '')) return;
  frm.set_value(field, value);
}

function crafted_schedule_calendar_color(frm) {
  const outlet = (frm.doc.outlet_name || '').trim();
  if (outlet && CRAFTED_OUTLET_CALENDAR_COLORS[outlet]) {
    return CRAFTED_OUTLET_CALENDAR_COLORS[outlet];
  }
  if (frm.doc.outlet_color) {
    return frm.doc.outlet_color;
  }
  // Open / unknown outlet fallback (keep previous open-green only when no outlet)
  if (!crafted_schedule_pref_name(frm)) {
    return '#2ec936';
  }
  return '#6c757d';
}

function crafted_schedule_apply_color(frm) {
  const next = crafted_schedule_calendar_color(frm);
  crafted_schedule_set_if_changed(frm, 'color', next);
}

function crafted_schedule_refresh_publish_buttons(frm) {
  frm.remove_custom_button(__('Publish Shift'));
  frm.remove_custom_button(__('Unpublish Shift'));
  if (frm.is_new()) return;
  if (!frm.doc.published) {
    frm.add_custom_button(__('Publish Shift'), () => {
      frm.set_value('published', 1).then(() => frm.save());
    });
  } else {
    frm.add_custom_button(__('Unpublish Shift'), () => {
      frm.set_value('published', 0).then(() => frm.save());
    });
  }
}
