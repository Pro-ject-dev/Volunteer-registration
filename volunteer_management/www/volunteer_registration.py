# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import frappe
from volunteer_management.volunteer_management.doctype.volunteer_registration_settings.volunteer_registration_settings import (
	VolunteerRegistrationSettings,
)


def get_context(context):
	context.no_cache = 1
	context.title = "Amma’s Birthday – Volunteer Registration"
	context.settings = frappe.get_single("Volunteer Registration Settings")
	context.stats = VolunteerRegistrationSettings.get_live_stats()
	return context

