import streamlit as st
from datetime import date

from database import (
    init_db,
    seed_demo_data,
    get_all_requests,
    get_request,
    create_request,
    create_activity,
    update_request_status,
    submit_requester_response,
    get_request_activity,
    get_triage,
)

REQUEST_STATUSES = [
    "Received",
    "Under Review",
    "Information Needed",
    "In Progress",
    "Completed",
]

st.set_page_config(
    page_title="Northstar Legal",
    page_icon="⚖️",
    layout="wide"
)

# -----------------------------
# DATABASE SETUP
# -----------------------------

init_db()
seed_demo_data()

# -----------------------------
# SESSION STATE
# -----------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_request_id" not in st.session_state:
    st.session_state.selected_request_id = None

if "submitted_request_id" not in st.session_state:
    st.session_state.submitted_request_id = None


# -----------------------------
# HELPERS
# -----------------------------

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()


def open_request(request_id):
    st.session_state.selected_request_id = request_id
    st.session_state.page = "request_details"
    st.rerun()


def render_request_summary_card(request, key_prefix):
    with st.container(border=True):
        left, right = st.columns([4, 1])

        with left:
            st.markdown(
                f"**{request['request_id']} — {request['title']}**"
            )

            details = request["status"]

            if request["deadline"]:
                details += f" · Deadline: {request['deadline']}"

            st.caption(details)

        with right:
            if st.button(
                "Open",
                key=f"{key_prefix}_{request['request_id']}"
            ):
                open_request(request["request_id"])


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:
    st.title("Northstar")
    st.caption("Legal Operations")

    if st.button("Home", use_container_width=True):
        go_to("home")

    if st.button("Ask Legal", use_container_width=True):
        go_to("ask_legal")

    if st.button("My Requests", use_container_width=True):
        go_to("my_requests")

    st.divider()

    st.caption("Northstar Legal")
    st.caption("Internal use only")


# -----------------------------
# HOME PAGE
# -----------------------------

if st.session_state.page == "home":

    requests = get_all_requests()

    st.title("Northstar Legal")
    st.caption("A centralized legal intake and workflow platform.")

    open_request_count = sum(
        request["status"] != "Completed"
        for request in requests
    )

    attention_requests = [
        request
        for request in requests
        if request["action_needed"] == 1
    ]

    completed_request_count = sum(
        request["status"] == "Completed"
        for request in requests
    )

    open_col, attention_col, completed_col = st.columns(3)

    with open_col:
        st.metric("Open Requests", open_request_count)

    with attention_col:
        st.metric("Needs Attention", len(attention_requests))

    with completed_col:
        st.metric("Completed", completed_request_count)

    if st.button("Create Request", type="primary"):
        go_to("ask_legal")

    st.header("Recent Requests", divider=True)

    recent_requests = requests[:3]

    if not recent_requests:
        st.info("No requests have been submitted yet.")

    for request in recent_requests:
        render_request_summary_card(request, "recent")

    st.header("Needs Your Attention", divider=True)

    if not attention_requests:
        st.success("Nothing needs your attention right now.")

    for request in attention_requests:
        with st.container(border=True):

            st.markdown(
                f"### {request['request_id']} — {request['title']}"
            )

            st.write(
                f"**Status:** {request['status']}"
            )

            if request["deadline"]:
                st.write(
                    f"**Deadline:** {request['deadline']}"
                )

            if request["status"] == "Information Needed":
                st.warning(
                    "Legal needs additional information from you."
                )
            else:
                st.info(
                    "New activity on this request."
                )

            if st.button(
                "View request",
                key=f"attention_{request['request_id']}"
            ):
                open_request(request["request_id"])

    st.header("All Requests", divider=True)

    for request in requests:
        render_request_summary_card(request, "open")


# -----------------------------
# ASK LEGAL PAGE
# -----------------------------

elif st.session_state.page == "ask_legal":

    st.title("Ask Legal")

    st.write(
        "Tell Legal what you need. "
        "You do not need to use legal terminology."
    )

    category = st.selectbox(
        "What is this about?",
        [
            "Choose a category",
            "Contracts & Commercial",
            "Vendors & Procurement",
            "Product & AI",
            "Privacy & Data",
            "Security & Incidents",
            "Employment & People",
            "IP & Brand",
            "Disputes, Litigation & Government",
            "Corporate & Governance",
            "I'm not sure",
        ]
    )

    description = st.text_area(
        "Tell Legal what you need",
        placeholder="Briefly describe your request...",
        height=140
    )

    st.subheader("Deadline")

    has_deadline = st.radio(
        "Is there a deadline?",
        ["No", "Yes"],
        horizontal=True
    )

    deadline = ""

    if has_deadline == "Yes":
        deadline_value = st.date_input(
            "Deadline",
            value=date.today()
        )

        deadline = deadline_value.strftime(
            "%B %d, %Y"
        )

        st.text_input(
            "Why does this date matter?",
            placeholder=(
                "Customer signing date, launch, "
                "government deadline..."
            )
        )

    urgent = st.checkbox(
        "I believe this request is urgent"
    )

    if urgent:
        st.text_area(
            "What could happen if this is not handled quickly?",
            placeholder=(
                "Briefly explain the business impact."
            )
        )

    sensitive = st.radio(
        "Does this request contain particularly sensitive information?",
        ["No", "Yes", "I'm not sure"],
        horizontal=True
    )

    # -----------------------------
    # CONDITIONAL QUESTIONS
    # -----------------------------

    if category == "Contracts & Commercial":

        st.subheader("Contract details")

        st.selectbox(
            "Where are you in the contract process?",
            [
                "Choose one",
                "Other company sent us their contract",
                "We sent them our standard contract",
                "They returned an edited/redlined version",
                "Terms have already been discussed or negotiated",
                "I'm not sure",
            ]
        )

        st.text_input(
            "Company / counterparty name"
        )

        st.text_input(
            "Approximate deal value",
            placeholder="Example: $180,000"
        )

        st.file_uploader(
            "Upload the contract or relevant document",
            type=["pdf", "doc", "docx"]
        )

    elif category == "Vendors & Procurement":

        st.subheader("Vendor details")

        st.text_input(
            "Vendor name"
        )

        st.radio(
            "Will this vendor receive or access customer, "
            "employee, or personal information?",
            ["No", "Yes", "I'm not sure"],
            horizontal=True
        )

        st.file_uploader(
            "Upload the vendor agreement if you have it",
            type=["pdf", "doc", "docx"]
        )

    elif category == "Privacy & Data":

        st.subheader("Privacy details")

        st.radio(
            "Does this involve information about customers, "
            "employees, users, or other people?",
            ["No", "Yes", "I'm not sure"],
            horizontal=True
        )

        st.text_area(
            "What information is involved?",
            placeholder=(
                "Describe it in normal business language."
            )
        )

    elif category == "Employment & People":

        st.subheader("People matter")

        st.info(
            "Sensitive employment requests may have restricted access."
        )

        st.selectbox(
            "What best describes the request?",
            [
                "Choose one",
                "General employment question",
                "Employee complaint",
                "Performance / discipline",
                "Hiring / offer",
                "Termination",
                "Workplace investigation",
                "Other",
            ]
        )

    elif category != "Choose a category":

        st.info(
            "This first version keeps the intake short. "
            "More category-specific questions can be added later."
        )

    st.divider()

    submitted = st.button(
        "Submit request",
        type="primary"
    )

    if submitted:

        if category == "Choose a category":
            st.error(
                "Please choose a category."
            )

        elif not description.strip():
            st.error(
                "Please briefly describe what you need."
            )

        else:

            title = description.strip()[:60]

            priority = (
                "Urgency flagged"
                if urgent
                else "Normal"
            )

            request_id = create_request(
                category=category,
                title=title,
                description=description.strip(),
                deadline=deadline,
                priority=priority,
                sensitive=sensitive,
            )

            st.session_state.selected_request_id = request_id
            st.session_state.submitted_request_id = request_id

    if st.session_state.submitted_request_id:
        submitted_request_id = st.session_state.submitted_request_id

        st.success(
            f"{submitted_request_id} was submitted successfully."
        )

        if st.button("View new request"):
            st.session_state.selected_request_id = submitted_request_id
            st.session_state.submitted_request_id = None
            go_to("request_details")


# -----------------------------
# MY REQUESTS PAGE
# -----------------------------

elif st.session_state.page == "my_requests":

    requests = get_all_requests()

    st.title("My Requests")

    search = st.text_input(
        "Search",
        placeholder=(
            "Search by company, request ID, or topic..."
        )
    )

    status_filter = st.selectbox(
        "Status",
        ["All", *REQUEST_STATUSES]
    )

    for request in requests:

        matches_search = (
            not search
            or search.lower()
            in request["title"].lower()
            or search.lower()
            in request["request_id"].lower()
            or search.lower()
            in request["description"].lower()
        )

        matches_status = (
            status_filter == "All"
            or request["status"] == status_filter
        )

        if matches_search and matches_status:

            with st.container(border=True):

                st.markdown(
                    f"### {request['request_id']} — "
                    f"{request['title']}"
                )

                st.write(
                    f"**Category:** {request['category']}"
                )

                st.write(
                    f"**Status:** {request['status']}"
                )

                if request["deadline"]:
                    st.write(
                        f"**Deadline:** {request['deadline']}"
                    )

                if st.button(
                    "Open request",
                    key=f"my_{request['request_id']}"
                ):
                    open_request(
                        request["request_id"]
                    )


# -----------------------------
# REQUEST DETAILS PAGE
# -----------------------------

elif st.session_state.page == "request_details":

    request_id = st.session_state.selected_request_id

    request = get_request(request_id)

    if request is None:

        st.warning(
            "No request selected."
        )

        if st.button("Back to Home"):
            go_to("home")

    else:

        if st.button("← Back"):
            go_to("home")

        st.caption(request["request_id"])
        st.title(request["title"])

        if st.session_state.pop("status_update_success", None) == request_id:
            st.success("Request status updated successfully.")

        if st.session_state.pop("response_submitted", None) == request_id:
            st.success("Your response was submitted to Legal.")

        st.header("Request Overview", divider=True)

        with st.container(border=True):
            status_col, priority_col, deadline_col = st.columns(3)

            with status_col:
                st.metric("Status", request["status"])

            with priority_col:
                st.metric("Priority", request["priority"])

            with deadline_col:
                st.metric("Deadline", request["deadline"] or "None")

            st.markdown(f"**Category**  \n{request['category']}")
            st.markdown(f"**Description**  \n{request['description']}")
            st.caption(f"Sensitive information: {request['sensitive']}")

        triage = get_triage(request)

        st.header("AI Triage", divider=True)

        with st.container(border=True):
            risk_col, suggested_col, team_col = st.columns(3)

            with risk_col:
                st.metric("Risk Level", triage["risk_level"])

            with suggested_col:
                st.metric("Suggested Priority", triage["suggested_priority"])

            with team_col:
                st.metric("Legal Team", triage["legal_team"])

            st.markdown("**Recommended Next Action**")
            st.write(triage["next_action"])

        st.header("Status Management", divider=True)

        with st.container(border=True):
            selected_status = st.selectbox(
                "Request status",
                REQUEST_STATUSES,
                index=REQUEST_STATUSES.index(request["status"]),
                key=f"status_{request_id}",
            )

            if st.button(
                "Update Status",
                key=f"update_status_{request_id}",
                type="primary"
            ):
                updated = update_request_status(
                    request_id,
                    selected_status,
                    int(selected_status == "Information Needed"),
                )

                if updated:
                    st.session_state.status_update_success = request_id
                    st.rerun()
                else:
                    st.error("The request could not be found.")

        st.header("Legal Comments", divider=True)

        with st.container(border=True):
            if st.session_state.pop("comment_posted", None) == request_id:
                st.success("Comment posted.")

            if st.session_state.pop("information_requested", None) == request_id:
                st.success("Additional information requested.")

            with st.form(
                f"legal_comment_{request_id}",
                clear_on_submit=True
            ):
                comment = st.text_area("Add a comment")
                post_comment = st.form_submit_button("Post Comment")

            if post_comment:
                comment_text = comment.strip()

                if comment_text:
                    create_activity(
                        request_id,
                        "comment",
                        comment_text
                    )
                    st.session_state.comment_posted = request_id
                    st.rerun()
                else:
                    st.error("Please enter a comment before posting.")

            if st.button(
                "Request Information",
                key=f"request_information_{request_id}"
            ):
                updated = update_request_status(
                    request_id,
                    "Information Needed",
                    1
                )

                if updated:
                    create_activity(
                        request_id,
                        "information_requested",
                        "Legal requested additional information."
                    )
                    st.session_state.information_requested = request_id
                    st.session_state.pop(f"status_{request_id}", None)
                    st.rerun()
                else:
                    st.error("The request could not be found.")

        st.header("Messages", divider=True)

        with st.container(border=True):
            st.text_area(
                "Message Legal",
                placeholder="Write a message...",
                key=f"message_{request['request_id']}"
            )

            if st.button("Send message"):
                st.success(
                    "Message added to the matter."
                )

        if request["status"] == "Information Needed":
            st.header("Requested Information", divider=True)

            with st.container(border=True):
                st.subheader("Provide Requested Information")

                with st.form(
                    f"requester_response_{request_id}",
                    clear_on_submit=True
                ):
                    response = st.text_area("Your response")
                    submit_response = st.form_submit_button("Submit Response")

                if submit_response:
                    response_text = response.strip()

                    if not response_text:
                        st.error("Please enter a response before submitting.")
                    elif submit_requester_response(request_id, response_text):
                        st.session_state.response_submitted = request_id
                        st.session_state.pop(f"status_{request_id}", None)
                        st.rerun()
                    else:
                        st.error("The response could not be submitted.")

        st.header("Activity", divider=True)

        activity = get_request_activity(request_id)

        if activity:
            for entry in activity:
                with st.container(border=True):
                    st.caption(entry["created_at"])
                    st.write(entry["description"])
        else:
            st.info("No activity has been recorded for this request yet.")
