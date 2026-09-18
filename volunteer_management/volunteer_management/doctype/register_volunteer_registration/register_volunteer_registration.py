# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import re
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, now_datetime


class RegisterVolunteerRegistration(Document):
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
				("school", _("Register School")),
				("year_of_study", _("Year of Study")),
				("enrollment_number", _("Enrollment Number")),
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
				("staff_school", _("Register School")),
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
					SELECT name FROM `tabRegister Volunteer Registration`
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

			settings = frappe.get_single("Register Volunteer Registration Settings")
			if self.participant_category == "Student" and not settings.registration_open_for_students:
				frappe.throw(_("Student volunteer registration is currently closed by the administrator."))
			if self.participant_category == "Staff" and not settings.registration_open_for_staff:
				frappe.throw(_("Staff volunteer registration is currently closed by the administrator."))

			now = now_datetime()
			opening_dt = get_datetime(settings.opening_date_time) if settings.opening_date_time else None
			closing_dt = get_datetime(settings.closing_date_time) if settings.closing_date_time else None

			if opening_dt and now < opening_dt:
				frappe.throw(_("Volunteer registration has not opened yet."))
			if closing_dt and now > closing_dt:
				frappe.throw(_("Volunteer registration has closed."))

	def validate_capacity(self):
		"""
		Unrestricted registration count: No capacity capping is enforced.
		Registrations remain open to all participants as long as registration window is active.
		"""
		return
