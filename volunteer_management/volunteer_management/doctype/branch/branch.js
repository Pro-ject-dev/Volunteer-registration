// Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
// For license information, please see license.txt

frappe.ui.form.on("Branch", {
	course: function(frm) {
		if (frm.doc.course) {
			frappe.db.get_value("Course", frm.doc.course, "school", function(r) {
				if (r && r.school) {
					frm.set_value("school", r.school);
				}
			});
		}
	}
});
