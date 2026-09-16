// Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
// For license information, please see license.txt

frappe.ui.form.on("Volunteer Registration", {
	refresh(frm) {
		frm.trigger("toggle_fields");
	},
	participant_category(frm) {
		frm.trigger("toggle_fields");
	},
	toggle_fields(frm) {
		const is_student = frm.doc.participant_category === "Student";
		const is_staff = frm.doc.participant_category === "Staff";

		frm.toggle_reqd("enrollment_number", is_student);
		frm.toggle_reqd("year_of_study", is_student);
		frm.toggle_reqd("course", is_student);
		frm.toggle_reqd("branch", is_student);
		frm.toggle_reqd("school", is_student);
		frm.toggle_reqd("faculty_name", is_student);
		frm.toggle_reqd("faculty_phone", is_student);

		frm.toggle_reqd("department", is_staff);
		frm.toggle_reqd("staff_school", is_staff);
		frm.toggle_reqd("contact_number", is_staff);
	}
});
