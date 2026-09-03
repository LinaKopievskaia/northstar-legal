# Northstar Legal

Northstar Legal is a lightweight legal operations intake and workflow platform designed to centralize legal requests, triage work, track status, manage follow-up questions, and provide visibility into the legal request lifecycle.

## Problem

Legal teams often receive requests through scattered email threads, Slack messages, meetings, and other informal channels. This makes it difficult to prioritize work, track ownership and status, collect missing information, and give business teams consistent visibility into progress.

## Solution

Northstar provides a single workflow for:

- Request intake
- Triage and prioritization
- Legal review
- Information requests
- Requester responses
- Status management
- Activity history
- Completion tracking

## Workflow

```text
Submit Request
      ↓
AI Triage
      ↓
Legal Review
      ↓
Information Needed (if required)
      ↓
Requester Response
      ↓
Under Review
      ↓
Completed
      ↓
Activity History / Dashboard
```

## Features

- Guided legal request intake across common legal categories
- My Requests view with search and status filtering
- Request Detail view with request, priority, deadline, and status information
- Rule-based, AI-style legal triage for risk, suggested priority, routing, and next steps
- Status management from receipt through completion
- Legal comments recorded in the request timeline
- Request Information workflow for legal follow-up
- Requester responses that return a request to review
- Timestamped activity history for submissions, status changes, comments, and responses
- Home dashboard metrics for open, attention-required, and completed work
- Recent Requests and attention queues
- Realistic demo legal operations scenarios

The current triage engine uses deterministic category, priority, and keyword rules. It does not make an OpenAI API call and is not GPT-powered.

## Tech Stack

- Python
- Streamlit
- SQLite
- Git and GitHub
- Streamlit Community Cloud

## Architecture

```text
Employee / Business Team
          ↓
      Ask Legal
          ↓
 Streamlit Application
          ↓
      SQLite DB
          ↓
Legal Triage + Workflow
          ↓
     Legal Review
          ↓
Status / Communication
          ↓
      Completion
```

The Streamlit application provides the interface and workflow controls. SQLite stores legal requests and their activity history, while the rule-based triage layer evaluates request details and recommends routing and next steps.

## Why I Built It

I built Northstar from the perspective of a legal professional transitioning into legal operations, privacy, AI governance, and legal technology. The project explores how straightforward product design and workflow automation can reduce fragmented intake, create clearer collaboration between Legal and business teams, and make legal work more visible without adding unnecessary complexity.

## Live Demo

[https://northstar-legal-b4dlywcpkpkw7jpmkgzgga.streamlit.app](https://northstar-legal-b4dlywcpkpkw7jpmkgzgga.streamlit.app)

## Future Improvements

- Authentication and role-based access
- Real LLM-powered triage
- Persistent document uploads
- Email and Slack notifications
- Legal operations analytics and reporting
- Dedicated privacy and vendor review workflows

## Disclaimer

Northstar Legal is a portfolio and demonstration project. It is not a production legal system and should not be used to manage confidential matters or relied upon for legal advice.
