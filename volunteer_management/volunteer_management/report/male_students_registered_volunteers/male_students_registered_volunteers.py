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
		{"label": _("Enrollment Number"), "fieldname": "enrollment_number", "fieldtype": "Data", "width": 160},
		{"label": _("Year of Study"), "fieldname": "year_of_study", "fieldtype": "Data", "width": 110},
		{"label": _("Course"), "fieldname": "course", "fieldtype": "Data", "width": 110},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Data", "width": 180},
		{"label": _("School"), "fieldname": "school", "fieldtype": "Data", "width": 180},
		{"label": _("Faculty-in-Charge"), "fieldname": "faculty_name", "fieldtype": "Data", "width": 160},
		{"label": _("Faculty Contact"), "fieldname": "faculty_phone", "fieldtype": "Data", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Registered At"), "fieldname": "registration_date_time", "fieldtype": "Datetime", "width": 150},
	]

	conditions = {"participant_group": "Male Students"}
	if status != "All":
		conditions["status"] = status

	data = frappe.get_all(
		"Volunteer Registration",
		filters=conditions,
		fields=[
			"name",
			"full_name",
			"enrollment_number",
			"year_of_study",
			"course",
			"branch",
			"school",
			"faculty_name",
			"faculty_phone",
			"status",
			"registration_date_time",
		],
		order_by="creation asc",
	)

	return columns, data
