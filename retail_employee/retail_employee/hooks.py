app_name = "retail_employee"
app_title = "Retail Employee"
app_publisher = "NARDO INC"
app_description = "Staff / employee portal for Crafted retail"
app_email = "it@nardo.ca"
app_license = "mit"

# After install, fixtures sync DocTypes / web forms / pages
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
                    "CRAFTED Store Roles",
                    "CRAFTED Employee Info",
                    "CRAFTED Store Schedule",
                    "CRAFTED Sales Targets",
                    "CRAFTED Sales Commissions",
                    "CRAFTED Employee Commissions Details",
                    "CRAFTED Register Closure",
                    "CRAFTED Register Closure Payments",
                    "CRAFTED Shift Type",
                    "CRAFTED Shift Assignment",
                    "CRAFTED Rooster Schedule",
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
        "filters": [
            ["name", "in", ["block-time-off", "employee-clock-in-out"]]
        ],
    },
]

website_route_rules = [
    {"from_route": "/staff", "to_route": "staff"},
]

# Prefer staff home for store roles (sites may also set role_home_page in another app)
# Documented here; enable on site if not already handled by consignor app.
# role_home_page = [
#     {"role": "Sales Associate", "home_page": "/staff"},
#     {"role": "Store Manager", "home_page": "/staff"},
#     {"role": "Consignor Manager", "home_page": "/staff"},
# ]
