import frappe

def create_doctype():
    doctype_name = "Register Study Year"
    
    # Check if exists
    if frappe.db.exists("DocType", doctype_name):
        print(f"DocType {doctype_name} already exists.")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": doctype_name,
        "module": "Volunteer Management",
        "custom": 0,
        "istable": 0,
        "naming_rule": "By fieldname",
        "autoname": "field:year_name",
        "fields": [
            {
                "fieldname": "year_name",
                "label": "Year Name",
                "fieldtype": "Data",
                "reqd": 1,
                "unique": 1,
                "in_list_view": 1
            }
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1
            },
            {
                "role": "Guest",
                "read": 1
            }
        ],
        "sort_field": "modified",
        "sort_order": "DESC"
    })
    doc.insert(ignore_permissions=True)
    print(f"DocType {doctype_name} created successfully.")

    # Populate default data
    default_years = ["2nd Year", "3rd Year", "4th Year", "5th Year", "Postgraduate", "PhD / Research", "Other"]
    for y in default_years:
        if not frappe.db.exists("Register Study Year", y):
            new_doc = frappe.get_doc({
                "doctype": "Register Study Year",
                "year_name": y
            })
            new_doc.insert(ignore_permissions=True)
    print("Default study years inserted.")
    frappe.db.commit()

if __name__ == "__main__":
    frappe.init(site="development.localhost")
    frappe.connect()
    create_doctype()
    frappe.destroy()
