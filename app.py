import streamlit as st
from datetime import date

from database import (
    init_db,
    seed_demo_data,
    get_all_requests,
    get_request,
    create_request,
    update_request_status,
)

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

    st.write(
        "Get help from Legal, track your requests, "
        "and access approved documents."
    )

    if st.button("➕ Ask Legal", type="primary"):
        go_to("ask_legal")

    st.divider()

    st.subheader("Needs your attention")

    attention_requests = [
        request
        for request in requests
        if request["action_needed"] == 1
    ]

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

    st.divider()

    st.subheader("Your requests")

    for request in requests:
        with st.container(border=True):

            left, right = st.columns([4, 1])

            with left:
                st.markdown(
                    f"**{request['request_id']} — {request['title']}**"
                )

                details = request["status"]

                if request["deadline"]:
                    details += (
                        f" · Deadline: {request['deadline']}"
                    )

                st.caption(details)

            with right:
                if st.button(
                    "Open",
                    key=f"open_{request['request_id']}"
                ):
                    open_request(
                        request["request_id"]
                    )


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

            st.success(
                f"{request_id} was submitted successfully."
            )

            if st.button("View new request"):
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
        [
            "All",
            "Received",
            "Under Review",
            "Information Needed",
            "Completed",
        ]
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

        st.caption(
            request["request_id"]
        )

        st.title(
            request["title"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Status",
                request["status"]
            )

        with col2:
            st.metric(
                "Priority",
                request["priority"]
            )

        with col3:
            st.metric(
                "Deadline",
                request["deadline"] or "None"
            )

        st.divider()

        st.subheader("Request")

        st.write(
            f"**Category:** {request['category']}"
        )

        st.write(
            request["description"]
        )

        st.write(
            f"**Sensitive:** {request['sensitive']}"
        )

        st.divider()

        st.subheader("Activity")

        if request["status"] == "Information Needed":

            st.warning(
                "Legal requested additional information."
            )

            response = st.text_area(
                "Your response"
            )

            response_file = st.file_uploader(
                "Upload requested documents",
                key=f"response_{request['request_id']}"
            )

            if st.button("Send response"):

                if response.strip() or response_file:

                    update_request_status(
                        request["request_id"],
                        "Under Review",
                        0
                    )

                    st.success(
                        "Your response was sent to Legal."
                    )

                    st.rerun()

                else:
                    st.error(
                        "Please add a response or upload a document."
                    )

        else:

            st.info(
                "There are no actions required from you right now."
            )

        st.divider()

        st.subheader("Messages")

        st.text_area(
            "Message Legal",
            placeholder="Write a message...",
            key=f"message_{request['request_id']}"
        )

        if st.button("Send message"):
            st.success(
                "Message added to the matter."
            )