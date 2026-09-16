# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import re
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, now_datetime


class VolunteerRegistration(Document):
	def validate(self):
		self.set_participant_group()
		self.validate_mandatory_fields()
		self.validate_contact_numbers()
		self.validate_duplicate_enrollment()
		self.validate_registration_window()
		self.validate_capacity()
		if not self.registration_date_time:
			self.registration_date_time = now_datetime()

	def set_participant_group(self):
		if not self.participant_category or not self.gender:
			frappe.throw(_("Participant Category and Gender are mandatory."))

		mapping = {
			("Student", "Female"): "Female Students",
			("Student", "Male"): "Male Students",
			("Staff", "Female"): "Female Staff",
			("Staff", "Male"): "Male Staff",
		}
		self.participant_group = mapping.get((self.participant_category, self.gender))
		if not self.participant_group:
			frappe.throw(_("Invalid Category '{0}' or Gender '{1}'.").format(
				self.participant_category, self.gender
			))

	def validate_mandatory_fields(self):
		if not self.full_name or not self.full_name.strip():
			frappe.throw(_("Full Name is mandatory."))
		self.full_name = self.full_name.strip()

		if self.participant_category == "Student":
			student_required = [
				("enrollment_number", _("Enrollment Number")),
				("year_of_study", _("Year of Study")),
				("course", _("Course")),
				("branch", _("Branch")),
				("school", _("School")),
				("faculty_name", _("Faculty-in-Charge Name")),
				("faculty_phone", _("Faculty-in-Charge Contact Number")),
			]
			for field, label in student_required:
				val = self.get(field)
				if not val or (isinstance(val, str) and not val.strip()):
					frappe.throw(_("{0} is mandatory for Student registration.").format(label))
				if isinstance(val, str):
					self.set(field, val.strip())

			# Clear staff fields
			self.department = None
			self.staff_school = None
			self.contact_number = None

		elif self.participant_category == "Staff":
			staff_required = [
				("department", _("Department")),
				("staff_school", _("School")),
				("contact_number", _("Contact Number")),
			]
			for field, label in staff_required:
				val = self.get(field)
				if not val or (isinstance(val, str) and not val.strip()):
					frappe.throw(_("{0} is mandatory for Staff registration.").format(label))
				if isinstance(val, str):
					self.set(field, val.strip())

			# Clear student fields
			self.enrollment_number = None
			self.year_of_study = None
			self.course = None
			self.branch = None
			self.school = None
			self.faculty_name = None
			self.faculty_phone = None

	def validate_contact_numbers(self):
		phone_to_check = None
		field_label = ""
		if self.participant_category == "Student":
			phone_to_check = self.faculty_phone
			field_label = _("Faculty-in-Charge Contact Number")
		elif self.participant_category == "Staff":
			phone_to_check = self.contact_number
			field_label = _("Contact Number")

		if phone_to_check:
			cleaned = re.sub(r"[\s\-\(\)]", "", str(phone_to_check))
			# Pattern matching Indian 10-digit number optionally prefixed with +91, 91, or 0
			match = re.match(r"^(?:\+91|91|0)?([6-9]\d{9})$", cleaned)
			if not match:
				frappe.throw(
					_("Invalid {0} '{1}'. Please provide a valid 10-digit mobile number.").format(
						field_label, phone_to_check
					)
				)
			# Store standardized 10-digit phone
			if self.participant_category == "Student":
				self.faculty_phone = match.group(1)
			else:
				self.contact_number = match.group(1)

	def validate_duplicate_enrollment(self):
		if self.participant_category == "Student" and self.enrollment_number:
			# Normalize Enrollment Number: uppercase and strip whitespace
			self.enrollment_number = self.enrollment_number.strip().upper()

			# Only Confirmed registrations block duplicate submissions
			if self.status == "Confirmed":
				existing = frappe.db.sql(
					"""
					SELECT name FROM `tabVolunteer Registration`
					WHERE UPPER(TRIM(enrollment_number)) = %s
					  AND status = 'Confirmed'
					  AND name != %s
					""",
					(self.enrollment_number, self.name or ""),
				)
				if existing:
					frappe.throw(
						_("A confirmed registration with Enrollment Number '{0}' already exists.").format(
							self.enrollment_number
						),
						frappe.DuplicateEntryError,
					)

	def validate_registration_window(self):
		# Only enforce window on new records or when transitioning to Confirmed
		if self.is_new() or (self.has_value_changed("status") and self.status == "Confirmed"):
			# Allow bypassing during automated tests if explicitly requested via frappe.flags
			if frappe.flags.in_test and frappe.flags.ignore_registration_window:
				return

			settings = frappe.get_single("Volunteer Registration Settings")
			if not settings.registration_open:
				frappe.throw(_("Volunteer registration is currently closed by the administrator."))

			now = now_datetime()
			opening_dt = get_datetime(settings.opening_date_time) if settings.opening_date_time else None
			closing_dt = get_datetime(settings.closing_date_time) if settings.closing_date_time else None

			if opening_dt and now < opening_dt:
				frappe.throw(_("Volunteer registration has not opened yet."))
			if closing_dt and now > closing_dt:
				frappe.throw(_("Volunteer registration has closed."))

	def validate_capacity(self):
		# Only Confirmed registrations consume capacity
		if self.status != "Confirmed":
			return

		# Check if we need to evaluate capacity (new doc, or status changed to Confirmed, or group changed)
		if (
			not self.is_new()
			and not self.has_value_changed("status")
			and not self.has_value_changed("participant_group")
		):
			return

		settings = frappe.get_single("Volunteer Registration Settings")

		# Obtain lock on settings to serialize simultaneous submissions and avoid race conditions
		frappe.db.sql("SELECT field FROM `tabSingles` WHERE `doctype` = 'Volunteer Registration Settings' LIMIT 1 FOR UPDATE")

		capacity_map = {
			"Female Students": cint(settings.female_student_capacity),
			"Male Students": cint(settings.male_student_capacity),
			"Female Staff": cint(settings.female_staff_capacity),
			"Male Staff": cint(settings.male_staff_capacity),
		}

		group_cap = capacity_map.get(self.participant_group, 0)

		# Immediate re-check of current confirmed registrations before insertion
		current_group_count = frappe.db.sql(
			"""
			SELECT COUNT(*) FROM `tabVolunteer Registration`
			WHERE participant_group = %s
			  AND status = 'Confirmed'
			  AND name != %s
			""",
			(self.participant_group, self.name or ""),
		)[0][0]

		if current_group_count >= group_cap:
			frappe.throw(
				_("{0} volunteer capacity is full ({1}/{2}). No further registrations can be accepted.").format(
					self.participant_group, current_group_count, group_cap
				),
				frappe.ValidationError,
			)

		total_cap = (
			capacity_map["Female Students"]
			+ capacity_map["Male Students"]
			+ capacity_map["Female Staff"]
			+ capacity_map["Male Staff"]
		)

		current_total_count = frappe.db.sql(
			"""
			SELECT COUNT(*) FROM `tabVolunteer Registration`
			WHERE status = 'Confirmed'
			  AND name != %s
			""",
			(self.name or "",),
		)[0][0]

		if current_total_count >= total_cap:
			frappe.throw(
				_("Overall volunteer capacity is full ({0}/{1}). No further registrations can be accepted.").format(
					current_total_count, total_cap
				),
				frappe.ValidationError,
			)
