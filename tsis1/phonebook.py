import csv
import json
from connect import get_connection


def execute_sql_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        sql = file.read()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def setup_database():
    execute_sql_file("schema.sql")
    execute_sql_file("procedures.sql")
    print("Database schema and procedures are ready.")


def get_or_create_group(cur, group_name):
    if not group_name:
        group_name = "Other"

    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )

    cur.execute(
        "SELECT id FROM groups WHERE name = %s",
        (group_name,)
    )

    return cur.fetchone()[0]


def add_contact(username, email=None, birthday=None, group_name="Other"):
    conn = get_connection()
    cur = conn.cursor()

    group_id = get_or_create_group(cur, group_name)

    cur.execute(
        """
        INSERT INTO contacts(username, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO UPDATE
        SET email = EXCLUDED.email,
            birthday = EXCLUDED.birthday,
            group_id = EXCLUDED.group_id
        RETURNING id
        """,
        (username, email or None, birthday or None, group_id)
    )

    contact_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return contact_id


def add_phone_to_contact(username, phone, phone_type):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "CALL add_phone(%s, %s, %s)",
            (username, phone, phone_type)
        )
        conn.commit()
        print("Phone added successfully.")
    except Exception as error:
        conn.rollback()
        print("Error:", error)

    cur.close()
    conn.close()


def move_contact_to_group(username, group_name):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "CALL move_to_group(%s, %s)",
            (username, group_name)
        )
        conn.commit()
        print("Contact moved successfully.")
    except Exception as error:
        conn.rollback()
        print("Error:", error)

    cur.close()
    conn.close()


def add_contact_console():
    username = input("Name: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday YYYY-MM-DD: ").strip()
    group_name = input("Group Family/Work/Friend/Other: ").strip()

    if group_name == "":
        group_name = "Other"

    add_contact(username, email, birthday, group_name)

    while True:
        phone = input("Phone number: ").strip()
        phone_type = input("Type home/work/mobile: ").strip()

        add_phone_to_contact(username, phone, phone_type)

        more = input("Add another phone? yes/no: ").strip().lower()
        if more != "yes":
            break


def search_contacts_console():
    query = input("Search name/email/phone/group: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM search_contacts(%s)",
        (query,)
    )

    rows = cur.fetchall()
    print_contacts(rows)

    cur.close()
    conn.close()


def filter_by_group():
    group_name = input("Group name: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            c.id,
            c.username,
            c.email,
            c.birthday,
            g.name,
            p.phone,
            p.type,
            c.date_added
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name ILIKE %s
        ORDER BY c.username
        """,
        (group_name,)
    )

    rows = cur.fetchall()
    print_contacts(rows)

    cur.close()
    conn.close()


def search_by_email():
    email_part = input("Email contains: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            c.id,
            c.username,
            c.email,
            c.birthday,
            g.name,
            p.phone,
            p.type,
            c.date_added
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.email ILIKE %s
        ORDER BY c.username
        """,
        (f"%{email_part}%",)
    )

    rows = cur.fetchall()
    print_contacts(rows)

    cur.close()
    conn.close()


def show_sorted_contacts():
    sort_by = input("Sort by username/birthday/date_added: ").strip()

    if sort_by not in ("username", "birthday", "date_added"):
        sort_by = "username"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        f"""
        SELECT
            c.id,
            c.username,
            c.email,
            c.birthday,
            g.name,
            p.phone,
            p.type,
            c.date_added
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY c.{sort_by}
        """
    )

    rows = cur.fetchall()
    print_contacts(rows)

    cur.close()
    conn.close()


def show_paginated_contacts():
    page_size = 5
    offset = 0

    sort_by = input("Sort by username/birthday/date_added: ").strip()

    if sort_by not in ("username", "birthday", "date_added"):
        sort_by = "username"

    conn = get_connection()
    cur = conn.cursor()

    while True:
        cur.execute(
            "SELECT * FROM get_contacts_page(%s, %s, %s)",
            (page_size, offset, sort_by)
        )

        rows = cur.fetchall()

        print("\n--- Page ---")
        if not rows:
            print("No contacts on this page.")
        else:
            for row in rows:
                print(row)

        command = input("\nnext / prev / quit: ").strip().lower()

        if command == "next":
            offset += page_size
        elif command == "prev":
            offset = max(0, offset - page_size)
        elif command == "quit":
            break
        else:
            print("Unknown command.")

    cur.close()
    conn.close()


def import_from_csv(filename="contacts.csv"):
    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            username = row["username"]
            email = row.get("email")
            birthday = row.get("birthday")
            group_name = row.get("group", "Other")
            phone = row.get("phone")
            phone_type = row.get("type", "mobile")

            group_id = get_or_create_group(cur, group_name)

            cur.execute(
                """
                INSERT INTO contacts(username, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (username) DO UPDATE
                SET email = EXCLUDED.email,
                    birthday = EXCLUDED.birthday,
                    group_id = EXCLUDED.group_id
                RETURNING id
                """,
                (username, email, birthday, group_id)
            )

            contact_id = cur.fetchone()[0]

            if phone:
                cur.execute(
                    """
                    INSERT INTO phones(contact_id, phone, type)
                    VALUES (%s, %s, %s)
                    """,
                    (contact_id, phone, phone_type)
                )

    conn.commit()
    cur.close()
    conn.close()

    print("CSV import finished.")


def export_to_json(filename="exported_contacts.json"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT c.id, c.username, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.username
        """
    )

    contacts = cur.fetchall()
    data = []

    for contact in contacts:
        contact_id, username, email, birthday, group_name = contact

        cur.execute(
            "SELECT phone, type FROM phones WHERE contact_id = %s",
            (contact_id,)
        )

        phones = cur.fetchall()

        data.append({
            "username": username,
            "email": email,
            "birthday": birthday.isoformat() if birthday else None,
            "group": group_name,
            "phones": [
                {
                    "phone": phone,
                    "type": phone_type
                }
                for phone, phone_type in phones
            ]
        })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    cur.close()
    conn.close()

    print(f"Exported to {filename}")


def import_from_json(filename="contacts.json"):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    conn = get_connection()
    cur = conn.cursor()

    for item in data:
        username = item.get("username")
        email = item.get("email")
        birthday = item.get("birthday")
        group_name = item.get("group", "Other")
        phones = item.get("phones", [])

        cur.execute(
            "SELECT id FROM contacts WHERE username = %s",
            (username,)
        )

        existing = cur.fetchone()

        if existing:
            choice = input(f"{username} already exists. skip or overwrite? ").strip().lower()

            if choice == "skip":
                continue

            contact_id = existing[0]
            group_id = get_or_create_group(cur, group_name)

            cur.execute(
                """
                UPDATE contacts
                SET email = %s,
                    birthday = %s,
                    group_id = %s
                WHERE id = %s
                """,
                (email, birthday, group_id, contact_id)
            )

            cur.execute(
                "DELETE FROM phones WHERE contact_id = %s",
                (contact_id,)
            )

        else:
            group_id = get_or_create_group(cur, group_name)

            cur.execute(
                """
                INSERT INTO contacts(username, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (username, email, birthday, group_id)
            )

            contact_id = cur.fetchone()[0]

        for phone_item in phones:
            cur.execute(
                """
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
                """,
                (
                    contact_id,
                    phone_item.get("phone"),
                    phone_item.get("type", "mobile")
                )
            )

    conn.commit()
    cur.close()
    conn.close()

    print("JSON import finished.")


def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return

    for row in rows:
        print(row)


def menu():
    while True:
        print("""
========== PHONEBOOK TSIS1 ==========
1. Setup database
2. Add contact
3. Add phone to existing contact
4. Move contact to group
5. Search contacts
6. Filter by group
7. Search by email
8. Sort contacts
9. Paginated contacts
10. Import from CSV
11. Export to JSON
12. Import from JSON
0. Exit
""")

        choice = input("Choose: ").strip()

        if choice == "1":
            setup_database()

        elif choice == "2":
            add_contact_console()

        elif choice == "3":
            username = input("Contact name: ").strip()
            phone = input("Phone: ").strip()
            phone_type = input("Type home/work/mobile: ").strip()
            add_phone_to_contact(username, phone, phone_type)

        elif choice == "4":
            username = input("Contact name: ").strip()
            group_name = input("New group: ").strip()
            move_contact_to_group(username, group_name)

        elif choice == "5":
            search_contacts_console()

        elif choice == "6":
            filter_by_group()

        elif choice == "7":
            search_by_email()

        elif choice == "8":
            show_sorted_contacts()

        elif choice == "9":
            show_paginated_contacts()

        elif choice == "10":
            filename = input("CSV filename: ").strip()
            if filename == "":
                filename = "contacts.csv"
            import_from_csv(filename)

        elif choice == "11":
            filename = input("JSON filename: ").strip()
            if filename == "":
                filename = "exported_contacts.json"
            export_to_json(filename)

        elif choice == "12":
            filename = input("JSON filename: ").strip()
            if filename == "":
                filename = "contacts.json"
            import_from_json(filename)

        elif choice == "0":
            break

        else:
            print("Wrong choice.")


if __name__ == "__main__":
    menu()