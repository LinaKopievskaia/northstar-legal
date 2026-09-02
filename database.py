import sqlite3

DB_NAME = "northstar.db"


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