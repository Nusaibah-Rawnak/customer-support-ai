import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "customers.db")

def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            plan TEXT,
            joined_date TEXT,
            country TEXT
        );

        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_date TEXT NOT NULL,
            resolved_date TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
    """)
    conn.commit()

def seed_data(conn):
    customers = [
        ("Ema Thompson", "ema.thompson@email.com", "+1-555-0101", "Premium", "2022-03-15", "USA"),
        ("James Carter", "james.carter@email.com", "+1-555-0102", "Basic", "2023-01-10", "USA"),
        ("Sofia Reyes", "sofia.reyes@email.com", "+52-555-0103", "Enterprise", "2021-07-22", "Mexico"),
        ("Liam Patel", "liam.patel@email.com", "+44-555-0104", "Premium", "2022-11-05", "UK"),
        ("Aisha Malik", "aisha.malik@email.com", "+92-555-0105", "Basic", "2023-06-18", "Pakistan"),
        ("Noah Williams", "noah.williams@email.com", "+1-555-0106", "Enterprise", "2020-09-30", "Canada"),
        ("Zara Ahmed", "zara.ahmed@email.com", "+971-555-0107", "Premium", "2022-05-14", "UAE"),
        ("Carlos Mendez", "carlos.mendez@email.com", "+34-555-0108", "Basic", "2023-08-25", "Spain"),
        ("Yuki Tanaka", "yuki.tanaka@email.com", "+81-555-0109", "Enterprise", "2021-12-01", "Japan"),
        ("Fatima Hassan", "fatima.hassan@email.com", "+20-555-0110", "Premium", "2022-09-19", "Egypt"),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO customers (name, email, phone, plan, joined_date, country)
        VALUES (?, ?, ?, ?, ?, ?)
    """, customers)
    conn.commit()

    tickets = [
        # Ema Thompson (id=1)
        (1, "Billing Overcharge", "I was charged twice for my subscription this month.", "Resolved", "High", "2024-01-10", "2024-01-12"),
        (1, "Cannot Access Dashboard", "Getting a 403 error when logging into the dashboard.", "Resolved", "Medium", "2024-03-22", "2024-03-23"),
        (1, "Request for Invoice", "Need a detailed invoice for Q1 2024 for tax purposes.", "Closed", "Low", "2024-04-01", "2024-04-02"),

        # James Carter (id=2)
        (2, "Password Reset Not Working", "Reset email is not arriving in inbox or spam.", "Resolved", "High", "2024-02-05", "2024-02-05"),
        (2, "Slow Loading Times", "App takes over 30 seconds to load on mobile.", "Open", "Medium", "2024-05-10", None),

        # Sofia Reyes (id=3)
        (3, "Feature Request: Dark Mode", "Would love a dark mode option in the settings.", "Closed", "Low", "2023-11-15", "2023-11-20"),
        (3, "Integration with Salesforce Failing", "The Salesforce sync stopped working after last update.", "In Progress", "High", "2024-04-18", None),
        (3, "Data Export Issue", "CSV export is missing the last 30 days of data.", "Resolved", "Medium", "2024-02-28", "2024-03-01"),

        # Liam Patel (id=4)
        (4, "Subscription Upgrade Question", "Want to know what's included in the Enterprise plan.", "Closed", "Low", "2024-01-20", "2024-01-21"),
        (4, "Two-Factor Auth Not Sending SMS", "2FA codes are not being received on my phone.", "Resolved", "High", "2024-03-10", "2024-03-11"),

        # Aisha Malik (id=5)
        (5, "Account Locked After Failed Logins", "Locked out after 3 attempts, need immediate access.", "Resolved", "High", "2024-05-01", "2024-05-01"),
        (5, "Incorrect Plan Shown", "My profile shows Basic but I upgraded to Premium last week.", "In Progress", "Medium", "2024-05-15", None),

        # Noah Williams (id=6)
        (6, "API Rate Limit Too Low", "Our integration is hitting rate limits daily.", "In Progress", "High", "2024-04-05", None),
        (6, "Missing Data in Reports", "Monthly reports show gaps for Feb 2024.", "Resolved", "Medium", "2024-03-15", "2024-03-18"),
        (6, "Custom Domain Setup Help", "Need assistance configuring custom domain for our portal.", "Closed", "Low", "2024-01-08", "2024-01-10"),

        # Zara Ahmed (id=7)
        (7, "Payment Method Update", "Need to update credit card on file.", "Resolved", "Low", "2024-02-14", "2024-02-14"),
        (7, "App Crashes on iOS 17", "The mobile app crashes immediately on launch on iOS 17.", "Open", "High", "2024-05-20", None),

        # Carlos Mendez (id=8)
        (8, "Language Setting Not Saving", "App keeps reverting to English despite setting Spanish.", "Open", "Medium", "2024-05-08", None),
        (8, "Refund Request", "Requesting refund for unused month due to service outage.", "In Progress", "High", "2024-05-12", None),

        # Yuki Tanaka (id=9)
        (9, "GDPR Data Deletion Request", "Please delete all personal data as per GDPR Article 17.", "Resolved", "High", "2024-03-05", "2024-03-15"),
        (9, "Enterprise SLA Response Time", "Our SLA guarantees 4hr response but last ticket took 2 days.", "Closed", "High", "2024-02-20", "2024-02-22"),
        (9, "Bulk User Import Failing", "CSV import for 500 users keeps timing out at 80%.", "In Progress", "Medium", "2024-05-18", None),

        # Fatima Hassan (id=10)
        (10, "Trial Extension Request", "Would like to extend trial by 2 weeks to complete evaluation.", "Closed", "Low", "2024-01-25", "2024-01-26"),
        (10, "Report Sharing Not Working", "Shared report links return 404 for external users.", "Resolved", "Medium", "2024-04-10", "2024-04-11"),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO support_tickets
        (customer_id, subject, description, status, priority, created_date, resolved_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, tickets)
    conn.commit()

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_data(conn)
    conn.close()
    print(f"Database created at {DB_PATH}")
    print("10 customers and 24 support tickets inserted.")