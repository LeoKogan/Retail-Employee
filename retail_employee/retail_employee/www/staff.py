# Employee website landing — mirrors erp.craftedgoods.ca Portal Settings custom_menu
import frappe

from consignor.permissions import is_staff
from consignor.portal import apply_portal_context, resolve_staff_consignor

# Title, route, short hint — same labels/routes as production Portal Settings
# (employee-facing subset Leonardo listed + My Account)
STAFF_CARDS = [
	("My Shifts", "/manage-shifts", "Your schedule"),
	("Tasks", "/my-tasks", "ToDos assigned to you"),
	("Block time Off", "/block-time-off", "Leave / time off"),
	("Clock In/Out", "/employee-clock-in-out", "Attendance check-in"),
	("Local Delivery", "https://merchant.trexity.com/", "Trexity merchant"),
	("Sales Goals", "/sales-goals", "Store goals"),
	("Online Store", "https://www.ecwid.com/", "Ecwid admin"),
	("POS System", "https://crafted.vendhq.com/signin/", "Lightspeed / Vend"),
	("Cash Counting", "/cashier-close", "Cashier close"),
	("Labels", "/label-creator", "Label Creator"),
	("My Account", "/me", "Account & portal home"),
]


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/staff"
		raise frappe.Redirect
	if not is_staff():
		frappe.local.flags.redirect_location = "/consignor/home"
		raise frappe.Redirect

	consignor = resolve_staff_consignor()
	apply_portal_context(context, consignor)
	context.title = "Staff portal"
	context.brand_html = "Crafted"
	context.full_name = frappe.utils.get_fullname(frappe.session.user) or frappe.session.user
	context.staff_cards = [
		{"title": t, "route": r, "hint": h} for (t, r, h) in STAFF_CARDS
	]
