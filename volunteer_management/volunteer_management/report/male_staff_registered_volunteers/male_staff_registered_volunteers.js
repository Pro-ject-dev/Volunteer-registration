// Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
// For license information, please see license.txt

frappe.query_reports["Male Staff Registered Volunteers"] = {
	"filters": [
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "Confirmed\nCancelled\nAll",
			"default": "Confirmed"
		}
	]
};

