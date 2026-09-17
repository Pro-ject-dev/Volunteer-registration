// Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
// For license information, please see license.txt

frappe.query_reports["Combined Volunteer Registration List"] = {
	"filters": [
		{
			"fieldname": "participant_group",
			"label": __("Participant Group"),
			"fieldtype": "Select",
			"options": "All\nFemale Students\nMale Students\nFemale Staff\nMale Staff",
			"default": "All"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "Confirmed\nCancelled\nAll",
			"default": "Confirmed"
		}
	]
};

