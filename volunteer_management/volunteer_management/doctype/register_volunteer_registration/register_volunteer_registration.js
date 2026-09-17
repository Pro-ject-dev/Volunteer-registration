// Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
// For license information, please see license.txt

frappe.ui.form.on("Register Volunteer Registration", {
	setup(frm) {
		frm.set_query("course", function() {
			return {
				filters: {
					school: frm.doc.school || "",
					disabled: 0
				}
			};
		});

		frm.set_query("branch", function() {
			return {
				filters: {
					course: frm.doc.course || "",
					disabled: 0
				}
			};
		});
	},

	refresh(frm) {
		frm.trigger("toggle_fields");
	},

	school(frm) {
		// When school changes, reset dependent course and branch
		if (frm.doc.course) {
			frm.set_value("course", "");
		}
		if (frm.doc.branch) {
			frm.set_value("branch", "");
		}
	},

	course(frm) {
		// When course changes, reset dependent branch
		if (frm.doc.branch) {
			frm.set_value("branch", "");
		}
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
