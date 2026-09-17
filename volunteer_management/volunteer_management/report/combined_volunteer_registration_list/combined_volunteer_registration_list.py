# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	status = filters.get("status") or "Confirmed"
	group = filters.get("participant_group")

	columns = [
		{"label": _("Registration ID"), "fieldname": "name", "fieldtype": "Link", "options": "Volunteer Registration", "width": 140},
		{"label": _("Full Name"), "fieldname": "full_name", "fieldtype": "Data", "width": 170},
		{"label": _("Category"), "fieldname": "participant_category", "fieldtype": "Data", "width": 90},
		{"label": _("Gender"), "fieldname": "gender", "fieldtype": "Data", "width": 80},
		{"label": _("Group"), "fieldname": "participant_group", "fieldtype": "Data", "width": 130},
		{"label": _("Enrollment / Dept"), "fieldname": "identifier", "fieldtype": "Data", "width": 180},
		{"label": _("Course / Branch"), "fieldname": "course_branch", "fieldtype": "Data", "width": 180},
		{"label": _("School"), "fieldname": "school_name", "fieldtype": "Data", "width": 180},
		{"label": _("Contact"), "fieldname": "contact", "fieldtype": "Data", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Registered At"), "fieldname": "registration_date_time", "fieldtype": "Datetime", "width": 150},
	]

	conditions = {}
	if status and status != "All":
		conditions["status"] = status
	if group and group != "All":
		conditions["participant_group"] = group

	raw_data = frappe.get_all(
		"Volunteer Registration",
		filters=conditions,
		fields=[
			"name",
			"full_name",
			"participant_category",
			"gender",
			"participant_group",
			"enrollment_number",
			"department",
			"course",
			"branch",
			"school",
			"staff_school",
			"faculty_phone",
			"contact_number",
			"status",
			"registration_date_time",
		],
		order_by="creation asc",
	)

	data = []
	for r in raw_data:
		identifier = r.enrollment_number if r.participant_category == "Student" else r.department
		course_branch = (
			f"{r.course} - {r.branch}" if r.participant_category == "Student" else (r.department or "")
		)
		school_name = r.school if r.participant_category == "Student" else r.staff_school
		contact = r.faculty_phone if r.participant_category == "Student" else r.contact_number

		data.append({
			"name": r.name,
			"full_name": r.full_name,
			"participant_category": r.participant_category,
			"gender": r.gender,
			"participant_group": r.participant_group,
			"identifier": identifier,
			"course_branch": course_branch,
			"school_name": school_name,
			"contact": contact,
			"status": r.status,
			"registration_date_time": r.registration_date_time,
		})

	return columns, data

