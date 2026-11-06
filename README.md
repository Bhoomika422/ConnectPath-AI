# ConnectPath AI — OAuth Setup Guide Builder

A focused product prototype for developers and agent builders who need to understand the work involved in creating and approving provider OAuth apps.

## What it does

- Shows a small curated OAuth guide library (Google, Slack, GitHub and Notion).
- Displays setup steps, difficulty, estimated setup time, possible approval delays, requirements and blockers.
- Separates work an agent can assist with from actions that require a human.
- Lets a user enter an unfamiliar app and an official documentation URL.
- Fetches the public documentation page and creates a shareable guide stored in SQLite.
- Optionally uses Gemini to synthesize the fetched source into a structured guide.

## Run locally

Requires Python 3.10+.

```bash
git clone <your-repository-url>
cd connectpath-ai
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and optionally add a Gemini API key.

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Start the app:

```bash
python app.py
```

Open http://127.0.0.1:5000

## AI research mode

Set `GEMINI_API_KEY` in `.env` to enable Gemini synthesis. Without a key, the app still fetches the submitted page and creates a transparent starter checklist. It labels unknown details as unverified rather than inventing provider-specific facts.

Never commit `.env` or provider credentials. The included `.gitignore` excludes it.

## Product decisions

1. **Focused library over 100 shallow entries:** four varied providers demonstrate distinct setup patterns while keeping the prototype verifiable.
2. **Evidence before confidence:** every curated guide links official provider documentation. Generated guides show the source page and state whether a console setup or approval was actually attempted.
3. **Human/agent boundary:** agents can research docs, draft checklists and validate configuration; humans must sign in, accept terms, own accounts and complete provider-specific reviews.
4. **Time estimates are ranges:** they are indicative prototype estimates for a straightforward development setup, not provider SLAs. Approval and verification can extend timelines.
5. **Shareable output:** generated guides receive a persistent local SQLite ID and a public route.

## Verification performed

- Curated guide content is linked to official documentation:
  - Google: https://developers.google.com/identity/protocols/oauth2
  - Slack: https://api.slack.com/authentication/oauth-v2
  - GitHub: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
  - Notion: https://developers.notion.com/docs/authorization
- The prototype does not sign in to provider consoles, create OAuth apps, request credentials, submit app reviews or complete provider approval.
- Dynamic guide generation verifies that the documentation page can be fetched. It does not independently prove that every generated statement is correct; review the linked sources before acting.

## Limitations / next steps

- The library contains four examples, not 100 apps.
- Dynamic research currently fetches one URL supplied by the user; it does not crawl an entire provider docs site or perform authenticated browser actions.
- Approval timelines and exact scope requirements are provider-, account- and use-case-specific. Unknowns are explicitly marked.
- SQLite is suitable for a local demo, not multi-instance production hosting. Use managed persistent storage for deployment.
- Add rate limiting, stronger SSRF protection, source snapshots, background jobs, tests and production secret management before public launch.
- For production, use a dedicated research/search API and cite each factual claim to the precise source section.

## Suggested demo script

1. Open the app directory and inspect the Google guide.
2. Compare Slack and GitHub setup differences.
3. Enter an unfamiliar provider name and its official OAuth documentation URL.
4. Generate the guide, inspect source/verification notes and open the shareable URL.
5. Explain which steps an agent can prepare and which require a human.

## Repository and deployment

Push this folder to GitHub. Deploy the Flask app to a Python-capable host. Configure `SECRET_KEY` and (optionally) `GEMINI_API_KEY` as environment variables. Use persistent storage for `data/guides.db`; ephemeral filesystems can erase generated share links after redeployment.
