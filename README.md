# ConnectPath AI — OAuth Setup Guide Builder

A focused product prototype that helps developers and AI agent builders understand the steps, requirements, timelines, and human approvals involved in setting up OAuth integrations with different providers.

## Live Demo

https://connectpath-ai.onrender.com

## GitHub Repository

https://github.com/Bhoomika422/ConnectPath-AI

## What It Does

ConnectPath AI helps users explore OAuth setup requirements through structured, easy-to-follow guides.

Key features:

- Provides a curated OAuth guide library for Google, Slack, GitHub, and Notion.
- Displays setup steps, difficulty levels, estimated setup time, possible approval delays, requirements, and common blockers.
- Separates tasks an AI agent can assist with from actions that require human involvement.
- Allows users to enter an unfamiliar application and provide its official OAuth documentation URL.
- Fetches publicly accessible documentation pages and generates shareable setup guides.
- Stores generated guides in SQLite.
- Optionally uses Gemini to synthesize fetched documentation into a structured guide.
- Clearly identifies unverified information instead of presenting assumptions as confirmed facts.

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **AI Integration:** Google Gemini API (optional)
- **Documentation Fetching:** Requests, BeautifulSoup
- **Deployment:** Render
- **Server:** Gunicorn

## Run Locally

### Prerequisites

- Python 3.10 or above
- Git
- A Gemini API key (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/Bhoomika422/ConnectPath-AI.git
cd ConnectPath-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows PowerShell**
```bash
venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`.

**Windows**
```bash
copy .env.example .env
```

**macOS/Linux**
```bash
cp .env.example .env
```

Add your configuration to `.env`:

```env
SECRET_KEY=your-secret-key
FLASK_DEBUG=false
GEMINI_API_KEY=your-gemini-api-key
```

The Gemini API key is optional. Never commit your actual `.env` file or API credentials to GitHub.

### 5. Start the Application

```bash
python app.py
```

Open the application at:

http://127.0.0.1:5000

## AI Research Mode

ConnectPath AI optionally uses the Gemini API to synthesize publicly fetched OAuth documentation into structured setup guidance.

When a Gemini API key is configured and the service is available, the application can use it to generate a structured guide.

If Gemini is unavailable or a request fails, the application can use its available fallback guidance. Fallback content should be treated as a starter reference, not as independently verified AI-generated research.

Users should always review the linked official documentation before acting on provider-specific requirements.

## Product Decisions

### 1. Focused Library Over 100 Shallow Entries

The prototype starts with four varied providers—Google, Slack, GitHub, and Notion—to demonstrate different OAuth setup patterns while keeping the initial library manageable and reviewable.

The structure can be extended to support a larger library of applications.

### 2. Evidence Before Confidence

Curated guides link to official provider documentation. Generated guides retain the documentation URL used as their source and distinguish known information from details that still need verification.

### 3. Human and Agent Responsibilities

AI agents can assist with researching documentation, drafting setup checklists, organizing requirements, and validating configuration.

Human involvement remains necessary for signing in, accepting terms, owning provider accounts, creating credentials, and completing provider-specific approval processes.

### 4. Transparent Time Estimates

Setup time estimates are indicative ranges for straightforward development scenarios. Actual timelines may vary depending on the provider, account type, requested permissions, and approval requirements.

### 5. Shareable Guides

Generated guides receive an identifier and can be accessed through a shareable application route.

## Official Documentation References

The curated guide library uses the following official documentation sources:

- **Google OAuth:** https://developers.google.com/identity/protocols/oauth2
- **Slack OAuth:** https://api.slack.com/authentication/oauth-v2
- **GitHub OAuth Apps:** https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
- **Notion Authorization:** https://developers.notion.com/docs/authorization

## Verification Performed

- Reviewed the official documentation links used by the curated guides.
- Tested the Flask application locally.
- Tested the deployed application on Render.
- Tested the guide generation flow using a publicly accessible documentation URL.
- Checked the generated guide and its shareable route.
- Confirmed that the prototype distinguishes source-based fallback guidance from AI-generated output when Gemini is unavailable.

The prototype does not sign in to provider consoles, create OAuth applications, request credentials, submit app reviews, or complete provider approval.

Fetching a documentation page does not independently verify every statement in a generated guide. Users should review the linked source before implementation.

## Limitations and Future Improvements

- The current curated library contains four providers, not 100 applications.
- Dynamic research currently fetches one documentation URL supplied by the user.
- It does not crawl an entire provider documentation website or perform authenticated browser actions.
- Gemini availability and response times depend on the external API.
- Approval timelines and exact permission requirements vary by provider, account, and use case.
- SQLite is suitable for this prototype but not ideal for multi-instance production hosting.
- Production improvements could include persistent managed storage, rate limiting, stronger SSRF protection, automated tests, background jobs, source snapshots, and more detailed source citations.
- A larger application library and dedicated research/search integration could improve coverage and source verification.

## Suggested Demo Walkthrough

1. Open the application and explore the curated OAuth guide library.
2. Inspect the Google OAuth guide.
3. Compare the Slack and GitHub setup requirements.
4. Enter an unfamiliar application name and its official OAuth documentation URL.
5. Generate a guide and inspect its setup steps, requirements, and verification notes.
6. Open the generated shareable guide.
7. Explain which tasks an AI agent can prepare and which actions require human approval.

## Deployment

The application is deployed on Render.

Live application: https://connectpath-ai.onrender.com

For deployment:

- Use a Python-compatible hosting platform.
- Install dependencies using `pip install -r requirements.txt`.
- Configure `SECRET_KEY` as an environment variable.
- Configure `GEMINI_API_KEY` if Gemini functionality is required.
- Use Gunicorn to serve the Flask application.
- Configure persistent storage for `data/guides.db` if generated guides need to survive redeployments.

## Project Links

- **Live Demo:** https://connectpath-ai.onrender.com
- **GitHub Repository:** https://github.com/Bhoomika422/ConnectPath-AI

---

**ConnectPath AI** — Making OAuth setup more understandable, structured, and transparent for developers and AI agents.
