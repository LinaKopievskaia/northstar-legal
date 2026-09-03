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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS request_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES legal_requests (request_id)
        )
        """
    )

    conn.commit()
    conn.close()


def seed_demo_data():
    conn = get_connection()
    cursor = conn.cursor()

    demo_requests = [
        {
            "request_id": "LEGAL-0101",
            "category": "Product & AI",
            "title": "Review AI meeting transcription vendor",
            "description": (
                "Business wants to use an AI transcription tool that will "
                "process employee meeting audio and notes."
            ),
            "status": "Under Review",
            "priority": "High",
            "action_needed": 0,
            "activities": [
                ("request_created", "Request submitted."),
                (
                    "status_changed",
                    "Status changed from Received to Under Review."
                ),
                ("review_started", "Legal started the vendor review."),
            ],
        },
        {
            "request_id": "LEGAL-0102",
            "category": "Privacy & Data",
            "title": "New customer analytics feature",
            "description": (
                "Product team wants to introduce analytics that collect user "
                "behavior and device information."
            ),
            "status": "Information Needed",
            "priority": "Normal",
            "action_needed": 1,
            "activities": [
                ("request_created", "Request submitted."),
                (
                    "status_changed",
                    "Status changed from Received to Information Needed."
                ),
                (
                    "information_requested",
                    "Legal requested additional information about data flows."
                ),
            ],
        },
        {
            "request_id": "LEGAL-0103",
            "category": "Contracts & Commercial",
            "title": "Enterprise SaaS agreement",
            "description": (
                "Sales needs review of a customer agreement with liability "
                "and data protection terms."
            ),
            "status": "Received",
            "priority": "High",
            "action_needed": 0,
            "activities": [
                ("request_created", "Request submitted."),
            ],
        },
        {
            "request_id": "LEGAL-0104",
            "category": "IP & Brand",
            "title": "Customer testimonial approval",
            "description": (
                "Marketing wants to publish a customer quote and logo on the "
                "company website."
            ),
            "status": "Completed",
            "priority": "Normal",
            "action_needed": 0,
            "activities": [
                ("request_created", "Request submitted."),
                (
                    "status_changed",
                    "Status changed from Received to Under Review."
                ),
                (
                    "status_changed",
                    "Status changed from Under Review to Completed."
                ),
            ],
        },
        {
            "request_id": "LEGAL-0105",
            "category": "Security & Incidents",
            "title": "Potential customer data exposure",
            "description": (
                "Security identified a configuration issue that may have "
                "exposed limited customer information."
            ),
            "status": "Under Review",
            "priority": "High",
            "action_needed": 0,
            "activities": [
                ("request_created", "Request submitted."),
                (
                    "status_changed",
                    "Status changed from Received to Under Review."
                ),
                ("review_started", "Legal and Security started incident review."),
            ],
        },
        {
            "request_id": "LEGAL-0106",
            "category": "Vendors & Procurement",
            "title": "New cloud storage provider",
            "description": (
                "Operations wants to onboard a cloud storage vendor that will "
                "handle internal company documents."
            ),
            "status": "Received",
            "priority": "Normal",
            "action_needed": 0,
            "activities": [
                ("request_created", "Request submitted."),
            ],
        },
    ]

    for demo in demo_requests:
        cursor.execute(
            "SELECT 1 FROM legal_requests WHERE title = ? LIMIT 1",
            (demo["title"],)
        )

        if cursor.fetchone():
            continue

        request_id = demo["request_id"]
        request_number = int(request_id.split("-")[-1])

        while cursor.execute(
            "SELECT 1 FROM legal_requests WHERE request_id = ?",
            (request_id,)
        ).fetchone():
            request_number += 1
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
                demo["category"],
                demo["title"],
                demo["description"],
                demo["status"],
                "",
                demo["priority"],
                demo["action_needed"],
                "No",
            )
        )

        for activity_type, description in demo["activities"]:
            _insert_activity(
                cursor,
                request_id,
                activity_type,
                description
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


def create_activity(request_id, activity_type, description):
    conn = get_connection()
    cursor = conn.cursor()

    _insert_activity(
        cursor,
        request_id,
        activity_type,
        description
    )

    conn.commit()
    conn.close()


def get_request_activity(request_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM request_activity
        WHERE request_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (request_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def _insert_activity(
    cursor,
    request_id,
    activity_type,
    description
):
    cursor.execute(
        """
        INSERT INTO request_activity (
            request_id,
            activity_type,
            description
        )
        VALUES (?, ?, ?)
        """,
        (request_id, activity_type, description)
    )


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

    _insert_activity(
        cursor,
        request_id,
        "request_created",
        "Request submitted."
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
        SELECT status
        FROM legal_requests
        WHERE request_id = ?
        """,
        (request_id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False

    previous_status = row["status"]

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

    if previous_status != status:
        _insert_activity(
            cursor,
            request_id,
            "status_changed",
            f"Status changed from {previous_status} to {status}."
        )

    conn.commit()
    conn.close()

    return True


def submit_requester_response(request_id, response):
    response = response.strip()

    if not response:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT status
        FROM legal_requests
        WHERE request_id = ?
        """,
        (request_id,)
    )

    row = cursor.fetchone()

    if row is None or row["status"] != "Information Needed":
        conn.close()
        return False

    _insert_activity(
        cursor,
        request_id,
        "requester_response",
        response
    )

    cursor.execute(
        """
        UPDATE legal_requests
        SET status = ?, action_needed = ?
        WHERE request_id = ?
        """,
        ("Under Review", 0, request_id)
    )

    _insert_activity(
        cursor,
        request_id,
        "status_changed",
        "Status changed from Information Needed to Under Review."
    )

    _insert_activity(
        cursor,
        request_id,
        "information_provided",
        "Requester provided additional information."
    )

    conn.commit()
    conn.close()

    return True


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
