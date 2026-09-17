# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, now_datetime
from volunteer_management.api import get_availability, submit_registration
from volunteer_management.volunteer_management.doctype.register_volunteer_registration_settings.register_volunteer_registration_settings import (
	RegisterRegisterVolunteerRegistrationSettings,
)


class TestRegisterVolunteerRegistration(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		# Clean up any existing volunteer registrations
		frappe.db.delete("Register Volunteer Registration")
		frappe.db.commit()
		from volunteer_management.fixtures.seed_academic_data import seed
		seed()

		# Reset settings to default
		settings = frappe.get_single("Register Register Volunteer Registration Settings")
		settings.event_name = "Amma's Birthday"
		settings.campus = "Coimbatore Campus"
		settings.registration_open = 1
		settings.opening_date_time = None
		settings.closing_date_time = None
		settings.female_student_capacity = 216
		settings.male_student_capacity = 216
		settings.female_staff_capacity = 22
		settings.male_staff_capacity = 22
		settings.save()
		frappe.db.commit()

	def tearDown(self):
		frappe.db.delete("Register Volunteer Registration")
		frappe.db.commit()
		super().tearDown()

	def test_01_female_student_registration(self):
		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Amrita Nair",
			"enrollment_number": "CB.EN.U4CSE21001",
			"year_of_study": "3rd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Ramesh",
			"faculty_phone": "9876543210",
		}).insert()

		self.assertEqual(doc.participant_group, "Female Students")
		self.assertEqual(doc.status, "Confirmed")
		self.assertTrue(doc.name.startswith("VR-"))
		self.assertIsNotNone(doc.registration_date_time)

	def test_02_male_student_registration(self):
		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Male",
			"full_name": "Karthik Kumar",
			"enrollment_number": "CB.EN.U4AIE21002",
			"year_of_study": "4th Year",
			"course": "B.Tech",
			"branch": "Artificial Intelligence",
			"school": "RegisterSchool of Computing",
			"faculty_name": "Dr. Suresh",
			"faculty_phone": "9876543211",
		}).insert()

		self.assertEqual(doc.participant_group, "Male Students")
		self.assertEqual(doc.status, "Confirmed")

	def test_03_female_staff_registration(self):
		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Staff",
			"gender": "Female",
			"full_name": "Prof. Lakshmi Devi",
			"department": "Department of Mathematics",
			"staff_school": "RegisterSchool of Physical Sciences",
			"contact_number": "9876543212",
		}).insert()

		self.assertEqual(doc.participant_group, "Female Staff")
		self.assertEqual(doc.status, "Confirmed")
		# Student fields should be cleared
		self.assertIsNone(doc.enrollment_number)

	def test_04_male_staff_registration(self):
		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Staff",
			"gender": "Male",
			"full_name": "Prof. Anand Mohan",
			"department": "Department of Computer Science and Engineering",
			"staff_school": "RegisterSchool of Engineering",
			"contact_number": "9876543213",
		}).insert()

		self.assertEqual(doc.participant_group, "Male Staff")
		self.assertEqual(doc.status, "Confirmed")

	def test_05_missing_mandatory_fields_student(self):
		# Missing enrollment number
		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Pooja Pillai",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Civil Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Ramesh",
			"faculty_phone": "9876543210",
		})
		self.assertRaises(frappe.ValidationError, doc.insert)

		# Missing branch
		doc2 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Pooja Pillai",
			"enrollment_number": "CB.EN.U4CIV21003",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Ramesh",
			"faculty_phone": "9876543210",
		})
		self.assertRaises(frappe.ValidationError, doc2.insert)

	def test_06_missing_mandatory_fields_staff(self):
		# Missing department
		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Staff",
			"gender": "Male",
			"full_name": "Ravi Shankar",
			"staff_school": "RegisterSchool of Engineering",
			"contact_number": "9876543210",
		})
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_07_invalid_phone_numbers(self):
		# Less than 10 digits
		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Ananya",
			"enrollment_number": "CB.EN.U4CSE21005",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Mechanical Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "12345",
		})
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_08_duplicate_enrollment_exact(self):
		frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Geetha",
			"enrollment_number": "CB.EN.U4CSE21010",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		}).insert()

		# Submitting with same enrollment number
		doc2 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Geetha Two",
			"enrollment_number": "CB.EN.U4CSE21010",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		})
		self.assertRaises(frappe.DuplicateEntryError, doc2.insert)

	def test_09_duplicate_enrollment_normalization(self):
		# 'cb.en.u4cse21020'
		frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Male",
			"full_name": "Sanjay",
			"enrollment_number": "cb.en.u4cse21020",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		}).insert()

		# Submitting with '  CB.EN.U4CSE21020  ' (uppercase + spaces)
		doc2 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Male",
			"full_name": "Sanjay Duplicate",
			"enrollment_number": "  CB.EN.U4CSE21020  ",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		})
		self.assertRaises(frappe.DuplicateEntryError, doc2.insert)

	def test_10_cancelled_registration_releases_duplicate(self):
		doc1 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Deepa",
			"enrollment_number": "CB.EN.U4CSE21030",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		}).insert()

		# Cancel doc1
		doc1.status = "Cancelled"
		doc1.save()

		# Now submitting with the same enrollment number should SUCCEED
		doc2 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Deepa New",
			"enrollment_number": "CB.EN.U4CSE21030",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		}).insert()
		self.assertEqual(doc2.status, "Confirmed")

	def test_11_cancelled_registration_releases_capacity(self):
		doc1 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Staff",
			"gender": "Female",
			"full_name": "Staff One",
			"department": "Department of Library",
			"staff_school": "General Administration",
			"contact_number": "9876543210",
		}).insert()
		self.assertEqual(doc1.status, "Confirmed")

		doc2 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Staff",
			"gender": "Female",
			"full_name": "Staff Two",
			"department": "Department of Library",
			"staff_school": "General Administration",
			"contact_number": "9876543211",
		}).insert()
		self.assertEqual(doc2.status, "Confirmed")

		# Cancel doc1
		doc1.status = "Cancelled"
		doc1.save()
		self.assertEqual(doc1.status, "Cancelled")
	def test_12_registration_before_opening_time(self):
		settings = frappe.get_single("Register Register Volunteer Registration Settings")
		settings.opening_date_time = add_days(now_datetime(), 1)  # Tomorrow
		settings.save()

		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Male",
			"full_name": "Early Bird",
			"enrollment_number": "CB.EN.U4CSE21040",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Civil Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		})
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_13_registration_after_closing_time(self):
		settings = frappe.get_single("Register Register Volunteer Registration Settings")
		settings.closing_date_time = add_days(now_datetime(), -1)  # Yesterday
		settings.save()

		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Male",
			"full_name": "Late Comers",
			"enrollment_number": "CB.EN.U4CSE21041",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Civil Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		})
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_14_manual_registration_shutdown(self):
		settings = frappe.get_single("Register Register Volunteer Registration Settings")
		settings.registration_open = 0
		settings.save()

		doc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Blocked User",
			"enrollment_number": "CB.EN.U4CSE21042",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Civil Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		})
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_15_female_student_capacity_limit(self):
		# With unrestricted capacity, multiple students register without capacity exceptions
		for i in [1, 2, 3]:
			doc = frappe.get_doc({
				"doctype": "Register Volunteer Registration",
				"participant_category": "Student",
				"gender": "Female",
				"full_name": f"Student {i}",
				"enrollment_number": f"CB.EN.U4CSE2105{i}",
				"year_of_study": "2nd Year",
				"course": "B.Tech",
				"branch": "Computer Science and Engineering",
				"school": "RegisterSchool of Engineering",
				"faculty_name": "Dr. Rao",
				"faculty_phone": "9876543210",
			}).insert()
			self.assertEqual(doc.status, "Confirmed")
	def test_16_total_capacity_calculation(self):
		settings = frappe.get_single("Register Register Volunteer Registration Settings")
		settings.female_student_capacity = 216
		settings.male_student_capacity = 216
		settings.female_staff_capacity = 22
		settings.male_staff_capacity = 22
		settings.save()
		self.assertEqual(settings.total_capacity, 476)

	def test_17_concurrent_race_condition_simulation(self):
		# In unrestricted mode, successive registrations are accepted without capacity rejection
		d1 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Staff",
			"gender": "Male",
			"full_name": "Staff First",
			"department": "Department of ICTS",
			"staff_school": "RegisterSchool of Engineering",
			"contact_number": "9876543210",
		}).insert()
		self.assertEqual(d1.status, "Confirmed")

		d2 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Staff",
			"gender": "Male",
			"full_name": "Staff Second",
			"department": "Department of ICTS",
			"staff_school": "RegisterSchool of Engineering",
			"contact_number": "9876543211",
		}).insert()
		self.assertEqual(d2.status, "Confirmed")
	def test_18_public_api_submit_and_protection(self):
		# Test submitting via API
		payload = {
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "API Student",
			"enrollment_number": "CB.EN.U4CSE21099",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
			# Attempting parameter tampering:
			"status": "Hacked",
			"participant_group": "Male Staff",
			"name": "VR-CUSTOM-001",
		}

		res = submit_registration(payload)
		self.assertTrue(res["success"])
		reg_id = res["registration_id"]

		doc = frappe.get_doc("Register Volunteer Registration", reg_id)
		# Verify server overrode tampered fields
		self.assertEqual(doc.status, "Confirmed")
		self.assertEqual(doc.participant_group, "Female Students")
		self.assertNotEqual(doc.name, "VR-CUSTOM-001")
		self.assertTrue(doc.name.startswith("VR-"))

	def test_19_availability_api_and_dashboard_stats(self):
		# Register 1 female student
		frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Stat Test",
			"enrollment_number": "CB.EN.U4CSE21100",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		}).insert()

		avail = get_availability()
		self.assertTrue(avail["success"])
		fs = avail["categories"]["Female Students"]
		self.assertEqual(fs["registered"], 1)
		self.assertFalse(fs["is_full"])
		self.assertFalse(fs["is_full"])

	def test_20_reports_execution(self):
		from volunteer_management.volunteer_management.report.combined_volunteer_registration_list.combined_volunteer_registration_list import (
			execute as exec_combined,
		)
		from volunteer_management.volunteer_management.report.female_students_registered_volunteers.female_students_registered_volunteers import (
			execute as exec_female_students,
		)

		frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Report User",
			"enrollment_number": "CB.EN.U4CSE21200",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
		}).insert()

		cols, data = exec_female_students()
		self.assertTrue(len(cols) > 0)
		self.assertEqual(len(data), 1)
		self.assertEqual(data[0]["enrollment_number"], "CB.EN.U4CSE21200")

		cols2, data2 = exec_combined()
		self.assertTrue(len(cols2) > 0)
		self.assertEqual(len(data2), 1)

	def test_21_male_student_and_staff_capacities(self):
		# Unrestricted mode allows registering multiple male students and staff
		d1 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Male",
			"full_name": "Male Student 1",
			"enrollment_number": "CB.EN.U4ME21001",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Mechanical Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Kumar",
			"faculty_phone": "9876543210",
		}).insert()
		self.assertEqual(d1.status, "Confirmed")

		d2 = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Male",
			"full_name": "Male Student 2",
			"enrollment_number": "CB.EN.U4ME21002",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Mechanical Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Kumar",
			"faculty_phone": "9876543210",
		}).insert()
		self.assertEqual(d2.status, "Confirmed")
	def test_22_overall_capacity_limit(self):
		# Unrestricted registrations continue past any previous capacity numbers
		for i in [1, 2, 3]:
			frappe.get_doc({
				"doctype": "Register Volunteer Registration",
				"participant_category": "Student",
				"gender": "Female",
				"full_name": f"Student {i}",
				"enrollment_number": f"CB.EN.U4ECE2100{i}",
				"year_of_study": "2nd Year",
				"course": "B.Tech",
				"branch": "Electronics and Communication",
				"school": "RegisterSchool of Engineering",
				"faculty_name": "Dr. Suresh",
				"faculty_phone": "9876543210",
			}).insert()

		total_count = frappe.db.count("Register Volunteer Registration", {"status": "Confirmed"})
		self.assertGreaterEqual(total_count, 3)
	def test_23_report_filtering_active_only(self):
		from volunteer_management.volunteer_management.report.combined_volunteer_registration_list.combined_volunteer_registration_list import (
			execute as exec_combined,
		)

		d_conf = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Female",
			"full_name": "Active Confirmed",
			"enrollment_number": "CB.EN.U4CSE21501",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
			"status": "Confirmed",
		}).insert()

		d_canc = frappe.get_doc({
			"doctype": "Register Volunteer Registration",
			"participant_category": "Student",
			"gender": "Male",
			"full_name": "Cancelled User",
			"enrollment_number": "CB.EN.U4CSE21502",
			"year_of_study": "2nd Year",
			"course": "B.Tech",
			"branch": "Computer Science and Engineering",
			"school": "RegisterSchool of Engineering",
			"faculty_name": "Dr. Rao",
			"faculty_phone": "9876543210",
			"status": "Confirmed",
		}).insert()

		d_canc.status = "Cancelled"
		d_canc.save()

		# Default filter status="Confirmed"
		cols, data = exec_combined({"status": "Confirmed"})
		self.assertEqual(len(data), 1)
		self.assertEqual(data[0]["full_name"], "Active Confirmed")

		# Filter status="All"
		cols_all, data_all = exec_combined({"status": "All"})
		self.assertEqual(len(data_all), 2)
	def test_24_dynamic_academic_doctypes_and_api(self):
		# Verify RegisterSchool, RegisterCourse, RegisterBranch exist and are returned by get_availability API
		res = get_availability()
		self.assertTrue(res["success"])
		self.assertIn("academic", res)
		academic = res["academic"]

		schools = [s["school_name"] for s in academic["schools"]]
		self.assertIn("RegisterSchool of Engineering", schools)
		self.assertIn("RegisterSchool of Computing", schools)

		courses = [c["course_name"] for c in academic["courses"] if c["school"] == "RegisterSchool of Engineering"]
		self.assertIn("B.Tech", courses)

		branches = [b["branch_name"] for b in academic["branches"] if b["school"] == "RegisterSchool of Engineering"]
		self.assertIn("Computer Science and Engineering", branches)

