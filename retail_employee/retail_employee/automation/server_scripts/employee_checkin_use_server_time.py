# Force Alberta (system) server time for Employee Clock In-Out web form punches.
# The web form client JS sets time from the phone clock and device_id from ipinfo.io as:
#   City|Region|Country|Postal|lat,lng|Timezone|IP|hostname
# Automatic Clock Out sets device_id == "Automatic Clock Out" and a scheduled end time — do not touch.
# Desk / HR / import punches without the ipinfo pipe pattern — do not touch.
# System timezone is America/Edmonton; frappe.utils.now_datetime() is Alberta local.

device_id = (doc.device_id or "").strip()
if device_id and ("|" in device_id) and device_id != "Automatic Clock Out":
    doc.time = frappe.utils.now_datetime()

# --- Link the punch to its Store Schedule shift (added 2026-11-09, approved by Leo) ---
# Same employee (Store Schedule.employee is the Employee Info name == Employee ID).
# A shift is a candidate when the punch falls between 3 h before its start and 4 h after its end.
# IN punches pick the shift whose start is closest; OUT punches the shift whose end is closest
# (so split shifts on the same day each get their own punches). Runs after the server-time fix above.
if not doc.get("store_schedule") and doc.employee and doc.time:
    ss_t = frappe.utils.get_datetime(doc.time)
    ss_cands = frappe.db.get_all("Store Schedule",
        filters=[["employee", "=", doc.employee],
                 ["time_in", "<=", frappe.utils.add_to_date(ss_t, hours=3)],
                 ["time_in", ">=", frappe.utils.add_to_date(ss_t, hours=-28)]],
        fields=["name", "time_in", "time_out"], order_by="time_in asc")
    ss_best = None
    ss_best_score = None
    for ss_s in ss_cands:
        ss_s_in = frappe.utils.get_datetime(ss_s.time_in)
        ss_s_out = frappe.utils.get_datetime(ss_s.time_out) if ss_s.time_out else frappe.utils.add_to_date(ss_s_in, hours=8)
        if ss_t < frappe.utils.add_to_date(ss_s_in, hours=-3) or ss_t > frappe.utils.add_to_date(ss_s_out, hours=4):
            continue
        ss_anchor = ss_s_out if doc.log_type == "OUT" else ss_s_in
        ss_score = abs(frappe.utils.time_diff_in_seconds(ss_t, ss_anchor))
        if ss_best_score is None or ss_score < ss_best_score:
            ss_best = ss_s.name
            ss_best_score = ss_score
    if ss_best:
        doc.store_schedule = ss_best
