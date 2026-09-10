app_name = "retail_employee"
app_title = "Retail Employee"
app_publisher = "NARDO INC"
app_description = "Staff / employee portal for Crafted retail"
app_email = "it@nardo.ca"
app_license = "mit"

fixtures = [
    {
        "dt": "DocType",
        "filters": [
            [
                "name",
                "in",
                [
                    "Outlets",
                    "Outlet Hours and Hard Target Sales",
                    "Outlet Duties",
                    "Store Roles",
                    "Employee Info",
                    "Store Schedule",
                    "Sales Targets",
                    "Sales Commissions",
                    "Employee Commissions Details",
                    "Register Closure",
                    "Register Closure Payments",
                    "Store Shift Type",
                    "Store Shift Assignment",
                    "Rooster Schedule",
                ],
            ]
        ],
    },
    {
        "dt": "Web Page",
        "filters": [
            [
                "name",
                "in",
                [
                    "manage-shifts",
                    "my-shifts",
                    "my-tasks",
                    "cashier-close",
                    "sales-goals",
                ],
            ]
        ],
    },
    {
        "dt": "Web Form",
        "filters": [["name", "in", ["block-time-off", "employee-clock-in-out"]]],
    },
]

website_route_rules = [
    {"from_route": "/staff", "to_route": "staff"},
]

role_home_page = {
    "Sales Associate": "staff",
    "Store Manager": "staff",
    "Consignor Manager": "staff",
}

doc_events = {
    "Employee Checkin": {
        "after_insert": "retail_employee.events.employee_checkin.after_insert",
    },
}

doctype_js = {
    "Store Schedule": "public/js/store_schedule.js",
}
