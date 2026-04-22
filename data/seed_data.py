import sqlite3
import os
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

DB_PATH = os.path.join(os.path.dirname(__file__), "customers.db")

PLANS = ["Basic", "Premium", "Enterprise"]
PLAN_WEIGHTS = [0.4, 0.35, 0.25]

STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
PRIORITIES = ["Low", "Medium", "High"]

CATEGORIES = ["Billing", "Technical", "Account", "Feature Request"]

AGENTS = [
    "Sarah Johnson",
    "Marcus Lee",
    "Priya Sharma",
    "Tom Bennett",
    "Anika Osei",
]

TICKET_TEMPLATES = {
    "Billing": [
        ("Incorrect Charge on Invoice", "I was charged twice for my subscription this month. Please review and issue a refund."),
        ("Refund Request", "I would like to request a refund for the unused portion of my current billing cycle."),
        ("Upgrade Billing Confusion", "After upgrading my plan, my invoice shows the wrong amount. Please clarify."),
        ("Payment Method Update", "I need to update my credit card on file as my old card has expired."),
        ("Unexpected Price Increase", "My bill increased this month without any notification. Please explain the change."),
        ("Invoice Not Received", "I did not receive my monthly invoice for the past two months."),
        ("Discount Not Applied", "The promotional discount I was promised during signup has not been applied."),
    ],
    "Technical": [
        ("App Crashes on Launch", "The mobile app crashes immediately after opening. I have tried reinstalling but the issue persists."),
        ("Slow Dashboard Loading", "The dashboard takes over 30 seconds to load. This started happening after the last update."),
        ("Data Export Failing", "Every time I try to export my data as CSV, the download fails at around 70%."),
        ("Integration Not Syncing", "My CRM integration stopped syncing 3 days ago. No data is being pulled through."),
        ("Login Issues After Password Reset", "After resetting my password I cannot log in. The system says my credentials are invalid."),
        ("Email Notifications Not Sending", "I am not receiving any email notifications despite having them enabled in settings."),
        ("API Rate Limit Errors", "Our integration is hitting rate limit errors even though we are well within our plan limits."),
        ("Bulk Import Timing Out", "Importing more than 200 records via CSV always times out before completing."),
        ("Two-Factor Authentication Not Working", "The 2FA code sent to my phone is always invalid. I cannot log in to my account."),
    ],
    "Account": [
        ("Cannot Update Profile Information", "I am unable to save changes to my profile. The save button does nothing."),
        ("Team Member Access Issue", "A new team member I added cannot access the shared workspace despite being invited."),
        ("GDPR Data Deletion Request", "Please delete all personal data associated with my account as per GDPR Article 17."),
        ("Account Ownership Transfer", "I need to transfer account ownership to a colleague as I am leaving the company."),
        ("Duplicate Account Merge Request", "I accidentally created two accounts with different emails and need them merged."),
        ("SSO Configuration Problem", "We are trying to set up SSO for our Enterprise account but keep getting configuration errors."),
        ("Username Change Request", "I would like to change my username but the option is greyed out in settings."),
    ],
    "Feature Request": [
        ("Dark Mode Support", "Please add a dark mode option to the dashboard. It would significantly reduce eye strain."),
        ("Bulk Action for Tickets", "It would be very helpful to be able to resolve or close multiple tickets at once."),
        ("Custom Report Builder", "We need the ability to create custom reports with filters specific to our business needs."),
        ("Mobile App Offline Mode", "An offline mode for the mobile app would be extremely useful when travelling."),
        ("Webhook Support", "We need webhook support so we can trigger automations when ticket statuses change."),
        ("Advanced Search Filters", "The current search is too basic. Please add filters for date range, agent, and category."),
        ("SLA Timer Visibility", "Please show the remaining SLA time directly on each ticket so agents can prioritize better."),
    ],
}

# Original 10 customers kept exactly as before so existing demo queries still work
ORIGINAL_CUSTOMERS = [
    ("Ema Thompson",  "ema.thompson@email.com",   "+1-555-0101",  "Premium",    "2022-03-15", "USA",      "Acme Corp",       4850.00, 4.2),
    ("James Carter",  "james.carter@email.com",   "+1-555-0102",  "Basic",      "2023-01-10", "USA",      "Carter LLC",      320.00,  3.8),
    ("Sofia Reyes",   "sofia.reyes@email.com",    "+52-555-0103", "Enterprise", "2021-07-22", "Mexico",   "Reyes Solutions", 12400.00, 4.7),
    ("Liam Patel",    "liam.patel@email.com",      "+44-555-0104", "Premium",    "2022-11-05", "UK",       "Patel Ventures",  5100.00, 4.0),
    ("Aisha Malik",   "aisha.malik@email.com",     "+92-555-0105", "Basic",      "2023-06-18", "Pakistan", "Malik Traders",   280.00,  3.5),
    ("Noah Williams", "noah.williams@email.com",   "+1-555-0106",  "Enterprise", "2020-09-30", "Canada",   "Williams Group",  18750.00, 4.9),
    ("Zara Ahmed",    "zara.ahmed@email.com",      "+971-555-0107","Premium",    "2022-05-14", "UAE",      "Ahmed Industries",4600.00, 4.3),
    ("Carlos Mendez", "carlos.mendez@email.com",   "+34-555-0108", "Basic",      "2023-08-25", "Spain",    "Mendez & Co",     290.00,  3.2),
    ("Yuki Tanaka",   "yuki.tanaka@email.com",     "+81-555-0109", "Enterprise", "2021-12-01", "Japan",    "Tanaka Tech",     15600.00, 4.6),
    ("Fatima Hassan", "fatima.hassan@email.com",   "+20-555-0110", "Premium",    "2022-09-19", "Egypt",    "Hassan Consulting",4200.00, 4.1),
]

ORIGINAL_TICKETS = [
    # Ema Thompson (id=1)
    (1, "Billing Discrepancy on March Invoice", "I was charged $299 instead of $199 for my Premium plan. Please review.", "Resolved", "High", "Billing", "Sarah Johnson", "2024-03-02", "2024-03-03", 18),
    (1, "Dashboard Not Loading After Update", "Since the latest update, my dashboard takes over 2 minutes to load or times out.", "Closed", "Medium", "Technical", "Marcus Lee", "2024-04-15", "2024-04-17", 36),
    (1, "Feature Request: Custom Report Export", "Would love the ability to schedule automated PDF exports of my monthly reports.", "Closed", "Low", "Feature Request", "Priya Sharma", "2024-02-10", "2024-02-12", 48),

    # James Carter (id=2)
    (2, "Can't Reset Password", "The reset password email never arrives even after multiple attempts.", "Resolved", "High", "Account", "Tom Bennett", "2024-05-01", "2024-05-01", 4),
    (2, "Unexpected Charge", "Charged for Premium plan but I am on Basic. Please refund the difference.", "In Progress", "High", "Billing", "Sarah Johnson", "2024-05-15", None, None),

    # Sofia Reyes (id=3)
    (3, "SSO Setup Failing", "Trying to configure SAML SSO for our Enterprise account but getting a 403 error.", "Resolved", "High", "Account", "Anika Osei", "2024-01-20", "2024-01-22", 28),
    (3, "API Rate Limiting Issue", "We are hitting rate limits despite being within the documented Enterprise limits.", "Closed", "High", "Technical", "Marcus Lee", "2024-02-28", "2024-03-01", 20),
    (3, "Request for Dedicated Account Manager", "As an Enterprise customer we would like a dedicated point of contact.", "Closed", "Low", "Feature Request", "Anika Osei", "2024-03-10", "2024-03-11", 24),

    # Liam Patel (id=4)
    (4, "Mobile App Crashes on iOS 17", "The app crashes immediately on launch since I updated to iOS 17.", "Open", "High", "Technical", "Marcus Lee", "2024-05-20", None, None),
    (4, "Discount Not Applied at Checkout", "I used a promo code during signup but the discount never appeared on my invoice.", "Resolved", "Medium", "Billing", "Sarah Johnson", "2024-04-05", "2024-04-06", 12),

    # Aisha Malik (id=5)
    (5, "Cannot Upload Profile Picture", "Every time I try to upload a profile picture I get a generic error message.", "Open", "Low", "Account", "Priya Sharma", "2024-05-10", None, None),
    (5, "Request: Dark Mode", "Please add a dark mode. Working at night is very straining on the eyes.", "Closed", "Low", "Feature Request", "Tom Bennett", "2024-01-08", "2024-01-10", 48),

    # Noah Williams (id=6)
    (6, "Enterprise SLA Breach", "Our SLA guarantees a 4-hour response but our last ticket took 2 business days.", "Resolved", "High", "Account", "Anika Osei", "2024-02-20", "2024-02-22", 10),
    (6, "Bulk User Import Timing Out", "Importing 500 users via CSV always fails at around 80% completion.", "In Progress", "Medium", "Technical", "Marcus Lee", "2024-05-18", None, None),
    (6, "Custom Webhook Integration", "We need webhook support to trigger our internal automations on ticket updates.", "Closed", "Medium", "Feature Request", "Anika Osei", "2024-03-15", "2024-03-16", 16),

    # Zara Ahmed (id=7)
    (7, "Payment Method Update", "Need to update the credit card on file as my old card expired.", "Resolved", "Low", "Billing", "Sarah Johnson", "2024-02-14", "2024-02-14", 2),
    (7, "App Crashes on iOS 17", "The mobile app crashes immediately on launch on iOS 17.", "Open", "High", "Technical", "Marcus Lee", "2024-05-20", None, None),

    # Carlos Mendez (id=8)
    (8, "Language Setting Not Saving", "App keeps reverting to English despite me setting Spanish in preferences.", "Open", "Medium", "Technical", "Tom Bennett", "2024-05-08", None, None),
    (8, "Refund Request for Service Outage", "Requesting a refund for the month affected by the service outage in April.", "In Progress", "High", "Billing", "Sarah Johnson", "2024-05-12", None, None),

    # Yuki Tanaka (id=9)
    (9, "GDPR Data Deletion Request", "Please delete all personal data associated with my account under GDPR Article 17.", "Resolved", "High", "Account", "Anika Osei", "2024-03-05", "2024-03-15", 240),
    (9, "Enterprise SLA Response Time", "Our SLA guarantees 4hr response but last ticket took 2 days.", "Closed", "High", "Account", "Anika Osei", "2024-02-20", "2024-02-22", 14),
    (9, "Bulk User Import Failing", "CSV import for 500 users keeps timing out at 80%.", "In Progress", "Medium", "Technical", "Marcus Lee", "2024-05-18", None, None),

    # Fatima Hassan (id=10)
    (10, "Trial Extension Request", "Would like to extend my trial by 2 weeks to complete our internal evaluation.", "Closed", "Low", "Account", "Priya Sharma", "2024-01-25", "2024-01-26", 8),
    (10, "Shared Report Links Return 404", "Report links shared with external stakeholders return a 404 error.", "Resolved", "Medium", "Technical", "Tom Bennett", "2024-04-10", "2024-04-11", 20),
]


def random_date(start_year=2020, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")


def generate_ticket(customer_id, joined_date_str):
    joined = datetime.strptime(joined_date_str, "%Y-%m-%d")
    ticket_start = joined + timedelta(days=random.randint(10, 60))
    days_available = (datetime(2024, 12, 31) - ticket_start).days
    days_available = max(days_available, 0)
    created = ticket_start + timedelta(days=random.randint(0, days_available))
    created_str = created.strftime("%Y-%m-%d")

    category = random.choice(CATEGORIES)
    subject, description = random.choice(TICKET_TEMPLATES[category])
    priority = random.choices(PRIORITIES, weights=[0.3, 0.45, 0.25])[0]
    agent = random.choice(AGENTS)

    # Older tickets more likely to be resolved/closed
    days_since_created = (datetime(2024, 12, 31) - created).days
    if days_since_created > 180:
        status = random.choices(STATUSES, weights=[0.05, 0.05, 0.45, 0.45])[0]
    elif days_since_created > 60:
        status = random.choices(STATUSES, weights=[0.15, 0.20, 0.35, 0.30])[0]
    else:
        status = random.choices(STATUSES, weights=[0.35, 0.35, 0.20, 0.10])[0]

    resolved_date = None
    resolution_time = None
    if status in ("Resolved", "Closed"):
        res_days = random.randint(1, 5)
        resolved_date = (created + timedelta(days=res_days)).strftime("%Y-%m-%d")
        resolution_time = random.randint(1, res_days * 24)

    return (
        customer_id, subject, description, status, priority,
        category, agent, created_str, resolved_date, resolution_time
    )


def create_tables(conn):
    conn.executescript("""
        DROP TABLE IF EXISTS support_tickets;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            name                TEXT NOT NULL,
            email               TEXT UNIQUE NOT NULL,
            phone               TEXT,
            plan                TEXT,
            joined_date         TEXT,
            country             TEXT,
            company             TEXT,
            account_value       REAL,
            satisfaction_score  REAL
        );

        CREATE TABLE support_tickets (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id          INTEGER NOT NULL,
            subject              TEXT NOT NULL,
            description          TEXT NOT NULL,
            status               TEXT NOT NULL,
            priority             TEXT NOT NULL,
            category             TEXT NOT NULL,
            agent_assigned       TEXT NOT NULL,
            created_date         TEXT NOT NULL,
            resolved_date        TEXT,
            resolution_time_hours INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
    """)
    conn.commit()


def seed_customers(conn):
    # Insert original 10 first
    conn.executemany("""
        INSERT OR IGNORE INTO customers
        (name, email, phone, plan, joined_date, country, company, account_value, satisfaction_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ORIGINAL_CUSTOMERS)

    # Generate 90 more with Faker to reach 100 total
    generated = []
    emails_seen = set(c[1] for c in ORIGINAL_CUSTOMERS)

    while len(generated) < 90:
        name = fake.name()
        email = fake.unique.email()
        if email in emails_seen:
            continue
        emails_seen.add(email)

        phone = fake.phone_number()[:20]
        plan = random.choices(PLANS, weights=PLAN_WEIGHTS)[0]
        joined_date = random_date(2019, 2024)
        country = fake.country()[:50]
        company = fake.company()[:80]

        if plan == "Enterprise":
            account_value = round(random.uniform(10000, 50000), 2)
        elif plan == "Premium":
            account_value = round(random.uniform(2000, 9999), 2)
        else:
            account_value = round(random.uniform(100, 1999), 2)

        satisfaction_score = round(random.uniform(2.0, 5.0), 1)

        generated.append((name, email, phone, plan, joined_date, country, company, account_value, satisfaction_score))

    conn.executemany("""
        INSERT OR IGNORE INTO customers
        (name, email, phone, plan, joined_date, country, company, account_value, satisfaction_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, generated)
    conn.commit()


def seed_tickets(conn):
    # Insert original tickets first
    conn.executemany("""
        INSERT INTO support_tickets
        (customer_id, subject, description, status, priority, category, agent_assigned,
         created_date, resolved_date, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ORIGINAL_TICKETS)

    # Generate tickets for all 100 customers
    cursor = conn.execute("SELECT id, joined_date FROM customers")
    customers = cursor.fetchall()

    tickets = []
    original_ids = set(range(1, 11))

    for customer_id, joined_date in customers:
        if customer_id in original_ids:
            continue  # already inserted above
        num_tickets = random.randint(3, 5)
        for _ in range(num_tickets):
            tickets.append(generate_ticket(customer_id, joined_date))

    conn.executemany("""
        INSERT INTO support_tickets
        (customer_id, subject, description, status, priority, category, agent_assigned,
         created_date, resolved_date, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets)
    conn.commit()
    return len(tickets) + len(ORIGINAL_TICKETS)


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Deleted old database at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_customers(conn)
    total_tickets = seed_tickets(conn)
    conn.close()

    print(f"Database created at {DB_PATH}")
    print(f"100 customers inserted (10 original + 90 generated)")
    print(f"{total_tickets} support tickets inserted")
    print()
    print("New columns added:")
    print("  customers:       company, account_value, satisfaction_score")
    print("  support_tickets: category, agent_assigned, resolution_time_hours")
    print()
    print("Example queries you can now ask:")
    print('  "Who are our highest value Enterprise customers?"')
    print('  "Which customers have a satisfaction score below 3?"')
    print('  "What is the average resolution time for high priority tickets?"')
    print('  "Which agent handles the most tickets?"')
    print('  "Show me all open billing tickets"')