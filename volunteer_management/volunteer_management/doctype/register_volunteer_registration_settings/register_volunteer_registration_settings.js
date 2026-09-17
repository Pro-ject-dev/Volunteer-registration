// Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
// For license information, please see license.txt

frappe.ui.form.on("Register Volunteer Registration Settings", {
	refresh(frm) {
		frm.trigger("calculate_total");
	},
	female_student_capacity(frm) {
		frm.trigger("calculate_total");
	},
	male_student_capacity(frm) {
		frm.trigger("calculate_total");
	},
	female_staff_capacity(frm) {
		frm.trigger("calculate_total");
	},
	male_staff_capacity(frm) {
		frm.trigger("calculate_total");
	},
	calculate_total(frm) {
		const total = (cint(frm.doc.female_student_capacity) || 0) +
			(cint(frm.doc.male_student_capacity) || 0) +
			(cint(frm.doc.female_staff_capacity) || 0) +
			(cint(frm.doc.male_staff_capacity) || 0);
		frm.set_value("total_capacity", total);
	}
});

