# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import frappe
from volunteer_management.volunteer_management.doctype.register_volunteer_registration_settings.register_volunteer_registration_settings import (
	RegisterVolunteerRegistrationSettings,
)


def get_context(context):
	context.no_cache = 1
	context.title = "Amma's Birthday – Volunteer Registration"
	context.settings = frappe.get_single("Register Volunteer Registration Settings")
	context.stats = RegisterVolunteerRegistrationSettings.get_live_stats()
	return context

