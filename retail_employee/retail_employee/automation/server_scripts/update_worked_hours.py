total_ts_hrs=0
total_expected_hrs= 0
total_extra_hrs= 0

for time_log in doc.time_logs:
    time_log.hours = round(frappe.utils.time_diff_in_hours(time_log.to_time,time_log.from_time),2)
    total_ts_hrs = total_ts_hrs + time_log.hours
    if bool(time_log.expected_hours):
        total_expected_hrs= total_expected_hrs + time_log.expected_hours
    if bool(time_log.extra_hrs):
        total_extra_hrs = total_extra_hrs + time_log.extra_hrs

doc.total_ts_hrs = round(total_ts_hrs,2)
doc.total_expected_hrs =round(total_expected_hrs,2)
doc.total_extra_hrs =round(total_extra_hrs,2)