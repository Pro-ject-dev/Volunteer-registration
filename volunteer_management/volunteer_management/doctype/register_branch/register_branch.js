// Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
// For license information, please see license.txt

frappe.ui.form.on("Register RegisterBranch", {
	course: function(frm) {
		if (frm.doc.course) {
			frappe.db.get_value("Register RegisterCourse", frm.doc.course, "school", function(r) {
				if (r && r.school) {
					frm.set_value("school", r.school);
				}
			});
		}
	}
});
