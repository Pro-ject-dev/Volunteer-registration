# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, now_datetime


class VolunteerRegistrationSettings(Document):
	def validate(self):
		# Enforce positive capacities
		for fld in [
			"female_student_capacity",
			"male_student_capacity",
			"female_staff_capacity",
			"male_staff_capacity",
		]:
			if cint(self.get(fld)) < 0:
				frappe.throw(frappe._("{0} cannot be negative.").format(self.meta.get_label(fld)))

		# Automatically calculate Total Capacity
		self.total_capacity = (
			cint(self.female_student_capacity)
			+ cint(self.male_student_capacity)
			+ cint(self.female_staff_capacity)
			+ cint(self.male_staff_capacity)
		)

	def onload(self):
		self.stats_html = self.get_stats_html()

	@staticmethod
	def get_live_stats():
		"""
		Calculates non-redundant derived statistics from confirmed Volunteer Registration records.
		"""
		settings = frappe.get_single("Volunteer Registration Settings")

		counts = {}
		# Query confirmed registrations grouped by participant_group
		group_counts = frappe.db.sql(
			"""
			SELECT participant_group, COUNT(*) as cnt
			FROM `tabVolunteer Registration`
			WHERE status = 'Confirmed'
			GROUP BY participant_group
			""",
			as_dict=True,
		)
		for row in group_counts:
			if row.participant_group:
				counts[row.participant_group] = row.cnt

		def make_group_stat(group_name, capacity):
			registered = counts.get(group_name, 0)
			remaining = max(0, capacity - registered)
			return {
				"group": group_name,
				"capacity": capacity,
				"registered": registered,
				"remaining": remaining,
				"is_full": registered >= capacity,
			}

		fs = make_group_stat("Female Students", cint(settings.female_student_capacity))
		ms = make_group_stat("Male Students", cint(settings.male_student_capacity))
		fst = make_group_stat("Female Staff", cint(settings.female_staff_capacity))
		mst = make_group_stat("Male Staff", cint(settings.male_staff_capacity))

		total_cap = fs["capacity"] + ms["capacity"] + fst["capacity"] + mst["capacity"]
		total_reg = fs["registered"] + ms["registered"] + fst["registered"] + mst["registered"]
		total_rem = max(0, total_cap - total_reg)

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
				"capacity": total_cap,
				"registered": total_reg,
				"remaining": total_rem,
				"is_full": total_reg >= total_cap,
			},
		}

	def get_stats_html(self):
		stats = self.get_live_stats()
		rows = ""
		for key, cat in stats["categories"].items():
			status_badge = (
				'<span class="indicator-pill red">FULL</span>'
				if cat["is_full"]
				else '<span class="indicator-pill green">Open</span>'
			)
			rows += f"""
			<tr>
				<td><strong>{cat['group']}</strong></td>
				<td style="text-align: right;">{cat['capacity']}</td>
				<td style="text-align: right; font-weight: bold;">{cat['registered']}</td>
				<td style="text-align: right;">{cat['remaining']}</td>
				<td style="text-align: center;">{status_badge}</td>
			</tr>
			"""

		tot = stats["total"]
		tot_badge = (
			'<span class="indicator-pill red">FULL</span>'
			if tot["is_full"]
			else '<span class="indicator-pill green">Open</span>'
		)

		return f"""
		<div style="padding: 10px 0;">
			<table class="table table-bordered table-striped" style="width: 100%; margin-top: 10px;">
				<thead>
					<tr style="background-color: #f8f9fa;">
						<th>Category</th>
						<th style="text-align: right;">Capacity</th>
						<th style="text-align: right;">Registered (Live)</th>
						<th style="text-align: right;">Remaining</th>
						<th style="text-align: center;">Status</th>
					</tr>
				</thead>
				<tbody>
					{rows}
					<tr style="background-color: #f1f3f5; font-weight: bold;">
						<td>Total</td>
						<td style="text-align: right;">{tot['capacity']}</td>
						<td style="text-align: right;">{tot['registered']}</td>
						<td style="text-align: right;">{tot['remaining']}</td>
						<td style="text-align: center;">{tot_badge}</td>
					</tr>
				</tbody>
			</table>
		</div>
		"""
