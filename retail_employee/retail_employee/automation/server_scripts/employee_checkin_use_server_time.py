# Force Alberta (system) server time for Employee Clock In-Out web form punches.
# The web form client JS sets time from the phone clock and device_id from ipinfo.io as:
#   City|Region|Country|Postal|lat,lng|Timezone|IP|hostname
# Automatic Clock Out sets device_id == "Automatic Clock Out" and a scheduled end time — do not touch.
# Desk / HR / import punches without the ipinfo pipe pattern — do not touch.
# System timezone is America/Edmonton; frappe.utils.now_datetime() is Alberta local.

device_id = (doc.device_id or "").strip()
if device_id and ("|" in device_id) and device_id != "Automatic Clock Out":
    doc.time = frappe.utils.now_datetime()
