# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import now_datetime
from volunteer_management.volunteer_management.doctype.register_volunteer_registration_settings.register_volunteer_registration_settings import (
	RegisterVolunteerRegistrationSettings,
)


@frappe.whitelist(allow_guest=True)
def get_availability():
	"""
	Exposes live registration statistics and dynamic academic hierarchy (Register School -> Register Course -> Register Branch).
	"""
	stats = RegisterVolunteerRegistrationSettings.get_live_stats()

	# Dynamic academic master options
	schools = frappe.get_all(
		"Register School",
		filters={"disabled": 0},
		fields=["name", "school_name"],
		order_by="school_name asc",
	)
	courses = frappe.get_all(
		"Register Course",
		filters={"disabled": 0},
		fields=["name", "course_name", "school"],
		order_by="course_name asc",
	)
	branches = frappe.get_all(
		"Register Branch",
		filters={"disabled": 0},
		fields=["name", "branch_name", "course", "school"],
		order_by="branch_name asc",
	)

	# Static/meta options for fields like year_of_study and department
	doc_meta = frappe.get_meta("Register Volunteer Registration")
	options = {}
	for fld_name in [
		"year_of_study",
		"department",
	]:
		field = doc_meta.get_field(fld_name)
		if field and field.options:
			options[fld_name] = [opt.strip() for opt in field.options.split("\n") if opt.strip()]

	# Map schools to master_options for backward compatibility
	options["school"] = [s.get("school_name") or s.get("name") for s in schools]
	options["staff_school"] = options["school"]

	stats["academic"] = {
		"schools": schools,
		"courses": courses,
		"branches": branches,
	}
	stats["master_options"] = options
	stats["success"] = True
	return stats


@frappe.whitelist(allow_guest=True)
def submit_registration(data=None):
	"""
	Public submission endpoint with strict server-side validation.
	Prevents client parameter tampering for status, registration ID, group, and timestamp.
	"""
	if frappe.request and frappe.request.method != "POST":
		frappe.throw(_("Invalid request method. POST expected."), frappe.ValidationError)

	if not data:
		if frappe.local.form_dict.get("data"):
			data = frappe.local.form_dict.get("data")
		else:
			data = frappe.local.form_dict

	if isinstance(data, str):
		try:
			data = json.loads(data)
		except Exception:
			frappe.throw(_("Invalid JSON payload."), frappe.ValidationError)

	if not isinstance(data, dict):
		frappe.throw(_("Invalid data format."), frappe.ValidationError)

	# Whitelist only participant-fillable fields
	allowed_fields = [
		"full_name",
		"participant_category",
		"gender",
		"enrollment_number",
		"year_of_study",
		"course",
		"branch",
		"school",
		"faculty_name",
		"faculty_phone",
		"department",
		"staff_school",
		"contact_number",
	]

	filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

	doc = frappe.new_doc("Register Volunteer Registration")
	doc.update(filtered_data)

	# Server sets authoritative system fields
	doc.status = "Confirmed"
	doc.registration_date_time = now_datetime()
	doc.ip_address = getattr(frappe.local, "request_ip", None)
	if hasattr(frappe, "request") and frappe.request and hasattr(frappe.request, "headers"):
		doc.user_agent = frappe.request.headers.get("User-Agent")

	# Insert doc with server-side validation
	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"success": True,
		"registration_id": doc.name,
		"full_name": doc.full_name,
		"participant_category": doc.participant_category,
		"gender": doc.gender,
		"participant_group": doc.participant_group,
		"registration_date_time": str(doc.registration_date_time),
		"enrollment_number": doc.enrollment_number if doc.participant_category == "Student" else None,
		"message": _("Registration confirmed successfully!"),
	}
