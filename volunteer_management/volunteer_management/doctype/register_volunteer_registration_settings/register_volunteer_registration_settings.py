# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, now_datetime


class RegisterVolunteerRegistrationSettings(Document):
	def validate(self):
		pass

	def onload(self):
		self.stats_html = self.get_stats_html()

	@staticmethod
	def get_live_stats():
		"""
		Calculates live registration statistics from confirmed Register Volunteer Registration records.
		No capacity capping or restrictions are enforced.
		Includes dynamic academic hierarchy for server-side template rendering.
		"""
		settings = frappe.get_single("Register Register Volunteer Registration Settings")

		counts = {}
		group_counts = frappe.db.sql(
			"""
			SELECT participant_group, COUNT(*) as cnt
			FROM `tabRegister Volunteer Registration`
			WHERE status = 'Confirmed'
			GROUP BY participant_group
			""",
			as_dict=True,
		)
		for row in group_counts:
			if row.participant_group:
				counts[row.participant_group] = row.cnt

		def make_group_stat(group_name):
			registered = counts.get(group_name, 0)
			return {
				"group": group_name,
				"registered": registered,
				"is_full": False,
			}

		fs = make_group_stat("Female Students")
		ms = make_group_stat("Male Students")
		fst = make_group_stat("Female Staff")
		mst = make_group_stat("Male Staff")

		total_reg = fs["registered"] + ms["registered"] + fst["registered"] + mst["registered"]

		# Check registration window
		now = now_datetime()
		is_open = bool(settings.registration_open)
		window_message = "Registration is open."

		opening_dt = get_datetime(settings.opening_date_time) if settings.opening_date_time else None
		closing_dt = get_datetime(settings.closing_date_time) if settings.closing_date_time else None

		if not is_open:
			window_message = "Registration is currently closed by the administrator."
		elif opening_dt and now < opening_dt:
			is_open = False
			window_message = f"Registration opens on {settings.opening_date_time}."
		elif closing_dt and now > closing_dt:
			is_open = False
			window_message = f"Registration closed on {settings.closing_date_time}."

		# Fetch dynamic academic hierarchy
		schools = frappe.get_all(
			"RegisterSchool",
			filters={"disabled": 0},
			fields=["name", "school_name"],
			order_by="school_name asc",
		)
		courses = frappe.get_all(
			"RegisterCourse",
			filters={"disabled": 0},
			fields=["name", "course_name", "school"],
			order_by="course_name asc",
		)
		branches = frappe.get_all(
			"RegisterBranch",
			filters={"disabled": 0},
			fields=["name", "branch_name", "course", "school"],
			order_by="branch_name asc",
		)

		return {
			"is_open": is_open,
			"window_message": window_message,
			"event_name": settings.event_name,
			"campus": settings.campus,
			"categories": {
				"Female Students": fs,
				"Male Students": ms,
				"Female Staff": fst,
				"Male Staff": mst,
			},
			"total": {
				"registered": total_reg,
				"is_full": False,
			},
			"academic": {
				"schools": schools,
				"courses": courses,
				"branches": branches,
			},
		}

	def get_stats_html(self):
		stats = self.get_live_stats()
		rows = ""
		for key, cat in stats["categories"].items():
			status_badge = '<span class="indicator-pill green">Open</span>'
			rows += f"""
			<tr>
				<td><strong>{cat['group']}</strong></td>
				<td style="text-align: right; font-weight: bold; font-size: 1.1em; color: #1a7a4a;">{cat['registered']}</td>
				<td style="text-align: center;">{status_badge}</td>
			</tr>
			"""

		tot = stats["total"]
		tot_badge = '<span class="indicator-pill green">Open</span>'

		return f"""
		<div style="padding: 10px 0;">
			<table class="table table-bordered table-striped" style="width: 100%; margin-top: 10px;">
				<thead>
					<tr style="background-color: #f8f9fa;">
						<th>Category</th>
						<th style="text-align: right;">Total Registered (Live)</th>
						<th style="text-align: center;">Status</th>
					</tr>
				</thead>
				<tbody>
					{rows}
					<tr style="background-color: #f1f3f5; font-weight: bold;">
						<td>Total Registered Volunteers</td>
						<td style="text-align: right; font-size: 1.15em; color: #7b1230;">{tot['registered']}</td>
						<td style="text-align: center;">{tot_badge}</td>
					</tr>
				</tbody>
			</table>
		</div>
		"""
