"""Upsert the local Server Script variants into a testing site (never run on production).

Copy into the bench (e.g. apps/frappe/frappe/_tmp_install.py) and run:
  bench --site crafted.localhost execute frappe._tmp_install.install --kwargs "{'path': '/tmp/server_scripts_local'}"
Requires server_script_enabled=1 in common_site_config.json (bench set-config -g server_script_enabled 1).
"""
import json, os
import frappe

FIELDS = ["script_type", "reference_doctype", "doctype_event", "event_frequency", "cron_format",
          "api_method", "allow_guest", "disabled", "module", "script"]

def install(path):
    assert "craftedgoods.ca" not in (frappe.local.site or ""), "refusing to run on production"
    out = []
    for fn in sorted(os.listdir(path)):
        if not fn.endswith(".json"):
            continue
        meta = json.load(open(os.path.join(path, fn)))
        name = meta["name"]
        vals = {k: meta.get(k) for k in FIELDS}
        if vals.get("module") and not frappe.db.exists("Module Def", vals["module"]):
            vals["module"] = None
        if frappe.db.exists("Server Script", name):
            doc = frappe.get_doc("Server Script", name)
            doc.update(vals)
            doc.save(ignore_permissions=True)
            out.append(("updated", name, doc.disabled))
        else:
            doc = frappe.get_doc(dict(doctype="Server Script", name=name, **vals))
            doc.insert(ignore_permissions=True)
            out.append(("inserted", name, doc.disabled))
    frappe.db.commit()
    for o in out:
        print(*o)
    return out
