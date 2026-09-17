# Copyright (c) 2026, Amrita Vishwa Vidyapeetham and contributors
# For license information, please see license.txt

import frappe

def seed():
    data = {
        "School of Engineering": {
            "B.Tech": [
                "Computer Science and Engineering",
                "Artificial Intelligence",
                "Electronics and Communication",
                "Electrical and Electronics",
                "Mechanical Engineering",
                "Civil Engineering",
                "Chemical Engineering",
                "Aerospace Engineering"
            ],
            "M.Tech": [
                "VLSI Design",
                "Power Electronics",
                "Thermal and Fluid Engineering",
                "Structural Engineering"
            ],
            "Ph.D (Engineering)": [
                "Engineering Sciences"
            ]
        },
        "School of Computing": {
            "BCA": [
                "Computer Applications",
                "Data Science"
            ],
            "MCA": [
                "Cyber Security"
            ],
            "Ph.D (Computing)": [
                "Computing Sciences"
            ]
        },
        "School of Business": {
            "BBA": [
                "General Management",
                "Business Analytics"
            ],
            "MBA": [
                "Finance",
                "Marketing",
                "Human Resources",
                "Operations"
            ],
            "Ph.D (Management)": [
                "Management Studies"
            ]
        },
        "School of Physical Sciences": {
            "B.Sc": [
                "Mathematics",
                "Physics",
                "Chemistry"
            ],
            "M.Sc": [
                "Applied Statistics"
            ],
            "Integrated M.Sc": [
                "Integrated Physical Sciences"
            ],
            "Ph.D (Sciences)": [
                "Physical Sciences"
            ]
        },
        "School of Arts, Humanities and Social Sciences": {
            "B.A": [
                "English Language and Literature",
                "Mass Communication"
            ],
            "M.A": [
                "Communication"
            ],
            "B.Com": [
                "Finance and Taxation"
            ],
            "M.Com": [
                "Commerce and Accounting"
            ],
            "MSW": [
                "Social Work"
            ],
            "Ph.D (Humanities)": [
                "Humanities and Social Sciences"
            ]
        },
        "General Administration": {},
        "School of Agricultural Sciences": {
            "B.Sc (Hons) Agriculture": [
                "Agricultural Sciences",
                "Horticulture"
            ],
            "M.Sc Agriculture": [
                "Agronomy",
                "Genetics and Plant Breeding"
            ],
            "Ph.D (Agriculture)": [
                "Agricultural Sciences Research"
            ]
        }
    }

    for school_name, courses in data.items():
        if not frappe.db.exists("School", school_name):
            s = frappe.get_doc({
                "doctype": "School",
                "school_name": school_name,
                "disabled": 0
            })
            s.insert(ignore_permissions=True)

        for course_name, branches in courses.items():
            if not frappe.db.exists("Course", course_name):
                c = frappe.get_doc({
                    "doctype": "Course",
                    "course_name": course_name,
                    "school": school_name,
                    "disabled": 0
                })
                c.insert(ignore_permissions=True)

            for branch_name in branches:
                if not frappe.db.exists("Branch", branch_name):
                    b = frappe.get_doc({
                        "doctype": "Branch",
                        "branch_name": branch_name,
                        "course": course_name,
                        "school": school_name,
                        "disabled": 0
                    })
                    b.insert(ignore_permissions=True)

    frappe.db.commit()

if __name__ == "__main__":
    frappe.init(site="development.localhost", sites_path="/home/vasudevan/frappe/frappe-bench/sites")
    frappe.connect()
    seed()
    print("Seed complete!")
    frappe.destroy()
