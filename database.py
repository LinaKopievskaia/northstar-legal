import sqlite3
import re
from pathlib import Path

DB_NAME = Path(__file__).resolve().with_name("northstar.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS legal_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            deadline TEXT,
            priority TEXT NOT NULL,
            action_needed INTEGER NOT NULL DEFAULT 0,
            sensitive TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def seed_demo_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM legal_requests"
    )

    count = cursor.fetchone()[0]

    if count == 0:
        demo_requests = [
            (
                "LEGAL-0071",
                "Contracts & Commercial",
                "Microsoft customer agreement",
                "Review Microsoft customer agreement.",
                "Information Needed",
                "September 4",
                "High",
                1,
                "No",
            ),
            (
                "LEGAL-0064",
                "Vendors & Procurement",
                "Vendor security review",
                "Review a new vendor.",
                "Under Review",
                "September 6",
                "Normal",
                1,
                "No",
            ),
            (
                "LEGAL-0062",
                "IP & Brand",
                "Marketing customer quote",
                "Approval to use customer quote.",
                "Completed",
                "",
                "Normal",
                0,
                "No",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO legal_requests (
                request_id,
                category,
                title,
                description,
                status,
                deadline,
                priority,
                action_needed,
                sensitive
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            demo_requests
        )

    conn.commit()
    conn.close()


def get_all_requests():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM legal_requests
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_request(request_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM legal_requests
        WHERE request_id = ?
        """,
        (request_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)

    return None


def create_request(
    category,
    title,
    description,
    deadline,
    priority,
    sensitive
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT MAX(id) FROM legal_requests"
    )

    max_id = cursor.fetchone()[0] or 0

    request_number = 80 + max_id + 1
    request_id = f"LEGAL-{request_number:04d}"

    cursor.execute(
        """
        INSERT INTO legal_requests (
            request_id,
            category,
            title,
            description,
            status,
            deadline,
            priority,
            action_needed,
            sensitive
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request_id,
            category,
            title,
            description,
            "Received",
            deadline,
            priority,
            0,
            sensitive,
        )
    )

    conn.commit()
    conn.close()

    return request_id


def update_request_status(
    request_id,
    status,
    action_needed=0
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE legal_requests
        SET status = ?, action_needed = ?
        WHERE request_id = ?
        """,
        (
            status,
            action_needed,
            request_id
        )
    )

    conn.commit()
    conn.close()


def get_triage(request):
    text = (
        f"{request.get('category', '')} "
        f"{request.get('description', '')}"
    ).lower()

    risk_level = "Low"
    suggested_priority = "Normal"
    legal_team = request.get("category") or "General Legal"
    next_action = "Legal should review the request and confirm next steps."

    high_risk_terms = [
        "breach",
        "security incident",
        "government",
        "subpoena",
        "lawsuit",
        "litigation",
        "termination",
        "personal data",
        "customer data",
        "employee data",
    ]

    medium_risk_terms = [
        "vendor",
        "contract",
        "agreement",
        "ai",
        "privacy",
        "data",
        "launch",
    ]

    def contains_any(terms):
        return any(
            re.search(rf"\b{re.escape(term)}\b", text)
            for term in terms
        )

    if contains_any(high_risk_terms):
        risk_level = "High"
        suggested_priority = "High"

    elif contains_any(medium_risk_terms):
        risk_level = "Medium"

    if request.get("priority") in {"High", "Urgency flagged"}:
        suggested_priority = "High"

    category = request.get("category")

    if category == "Privacy & Data":
        next_action = (
            "Identify the personal data involved, the purpose of processing, "
            "and whether a privacy review or DPIA is required."
        )

    elif category == "Product & AI":
        next_action = (
            "Review the product use case, data flows, AI risks, "
            "and applicable product or privacy requirements."
        )

    elif category == "Vendors & Procurement":
        next_action = (
            "Review the vendor agreement, data access, security requirements, "
            "and whether a privacy or security assessment is needed."
        )

    elif category == "Contracts & Commercial":
        next_action = (
            "Review the agreement, identify material deviations, "
            "and confirm the business deadline and deal context."
        )

    elif category == "Security & Incidents":
        next_action = (
            "Escalate for legal and security review and preserve "
            "relevant incident information."
        )

    return {
        "risk_level": risk_level,
        "suggested_priority": suggested_priority,
        "legal_team": legal_team,
        "next_action": next_action,
    }
