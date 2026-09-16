# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	status = filters.get("status") or "Confirmed"

	columns = [
		{"label": _("Registration ID"), "fieldname": "name", "fieldtype": "Link", "options": "Volunteer Registration", "width": 150},
		{"label": _("Full Name"), "fieldname": "full_name", "fieldtype": "Data", "width": 180},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 200},
		{"label": _("School"), "fieldname": "staff_school", "fieldtype": "Data", "width": 200},
		{"label": _("Contact Number"), "fieldname": "contact_number", "fieldtype": "Data", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Registered At"), "fieldname": "registration_date_time", "fieldtype": "Datetime", "width": 150},
	]

	conditions = {"participant_group": "Female Staff"}
	if status != "All":
		conditions["status"] = status

	data = frappe.get_all(
		"Volunteer Registration",
		filters=conditions,
		fields=[
			"name",
			"full_name",
			"department",
			"staff_school",
			"contact_number",
			"status",
			"registration_date_time",
		],
		order_by="creation asc",
	)

	return columns, data
