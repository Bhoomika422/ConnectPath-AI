import os
import re
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, abort

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")
DB_PATH = os.path.join(app.root_path, "data", "guides.db")
DATA_PATH = os.path.join(app.root_path, "data", "apps.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    APP_LIBRARY = json.load(f)

def db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS guides (
                id TEXT PRIMARY KEY,
                app_name TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

def safe_http_url(value):
    try:
        p = urlparse(value.strip())
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def fetch_page(url):
    """Fetch a public documentation page. Never fetch localhost/private network targets."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    blocked = (
        host in {"localhost", "127.0.0.1", "::1"} or
        host.startswith("10.") or host.startswith("192.168.") or
        host.startswith("172.16.") or host.endswith(".local")
    )
    if not safe_http_url(url) or blocked:
        raise ValueError("Enter a public http(s) documentation URL.")
    response = requests.get(
        url, timeout=12, headers={"User-Agent": "ConnectPathResearch/1.0"}
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else url
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    return title, text[:14000]

def make_ai_guide(app_name, url, title, source_text):
    """Use Gemini when configured; otherwise return an honest evidence-led draft."""
    api_key = os.getenv("GEMINI_API_KEY")
    ai_error = "GEMINI_API_KEY is not configured."
    if api_key:
        prompt = f"""
You are a careful OAuth integration research assistant.
Create a practical guide for a developer setting up an OAuth app for: {app_name}.
Use only the source material below. Do not invent exact console menu names, review times,
scopes, or requirements. If missing, say "Not verified — check provider documentation".
Return ONLY valid JSON with keys:
summary, difficulty (Easy/Moderate/Hard/Unknown), estimated_time,
approval_wait, steps (array of objects with title, detail, owner where owner is Agent/Human),
requirements (array), blockers (array), agent_can_do (array), human_must_do (array),
verification_notes, sources (array of objects with label,url).
Source title: {title}
Source URL: {url}
Source material:
{source_text}
"""
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
        try:
            r = requests.post(
                endpoint + "?key=" + api_key,
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}},
                timeout=30
            )
            r.raise_for_status()
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            data = json.loads(raw)
            data["app_name"] = app_name
            data["sources"] = data.get("sources") or [{"label": title, "url": url}]
            data["sources"].append({"label": "Submitted documentation page", "url": url})
            data["research_mode"] = "AI-assisted source analysis"
            return data
        except Exception as exc:
            if isinstance(exc, requests.HTTPError) and exc.response is not None:
                try:
                    message = exc.response.json().get("error", {}).get("message", "No details")
                except Exception:
                    message = "Could not read error details"
                ai_error = f"Gemini HTTP {exc.response.status_code}: {message[:300]}"
            else:
                ai_error = f"Gemini request failed: {type(exc).__name__}"
    

    if "linear.app" in url.lower() or app_name.strip().lower() == "linear":
        return {
            "app_name": app_name,
            "summary": "Linear supports OAuth 2.0 for third-party integrations. This guide uses Linear's official developer documentation.",
            "difficulty": "Moderate",
            "estimated_time": "Not officially specified. Allow time for app registration, implementation and end-to-end testing.",
            "approval_wait": "Not specified in the submitted documentation. Verify any distribution or workspace-specific requirements.",
            "steps": [
                {
                    "title": "Create a Linear OAuth application",
                    "detail": "Create an OAuth2 Application in Linear. Linear recommends using a dedicated workspace to manage the application. Configure your redirect callback URL.",
                    "owner": "Human"
                },
                {
                    "title": "Configure the authorization request",
                    "detail": "Redirect users to https://linear.app/oauth/authorize. Include client_id, redirect_uri, response_type=code and scope. The read scope is always present. Add state to protect against CSRF.",
                    "owner": "Agent"
                },
                {
                    "title": "Choose permissions and PKCE",
                    "detail": "Request only necessary scopes. Available scopes include read, write, issues:create, comments:create and timeSchedule:write. Avoid admin unless essential. Linear supports PKCE; use S256 with a generated code challenge.",
                    "owner": "Agent"
                },
                {
                    "title": "Handle the OAuth callback",
                    "detail": "Receive the authorization code at your registered redirect URI. Compare the returned state with the original state before trusting the callback.",
                    "owner": "Agent"
                },
                {
                    "title": "Exchange the authorization code",
                    "detail": "POST to https://api.linear.app/oauth/token using application/x-www-form-urlencoded. Send code, redirect_uri, client_id and grant_type=authorization_code. Include client_secret unless using the PKCE flow where it is optional, and send the code_verifier.",
                    "owner": "Agent"
                },
                {
                    "title": "Store and refresh tokens securely",
                    "detail": "Store access and refresh tokens securely. Linear documents access tokens as valid for 24 hours. Use the refresh_token grant at the token endpoint to obtain new tokens when needed.",
                    "owner": "Agent"
                },
                {
                    "title": "Test the integration",
                    "detail": "Test authorization, callback state validation, token exchange, refresh and a permitted GraphQL API request. Never expose client secrets or tokens.",
                    "owner": "Human"
                }
            ],
            "requirements": [
                "A Linear workspace and OAuth2 application.",
                "A registered redirect callback URL.",
                "Client ID and client secret, unless using the supported PKCE configuration where the secret is optional during token exchange.",
                "A clearly defined minimum set of OAuth scopes.",
                "Secure storage for access and refresh tokens."
            ],
            "blockers": [
                "Incorrect redirect URI can prevent successful authorization.",
                "A missing or mismatched state value must cause the callback to be rejected.",
                "Insufficient scopes can prevent requested API operations.",
                "Workspace and distribution requirements should be checked before public release."
            ],
            "agent_can_do": [
                "Prepare the authorization URL and required parameters.",
                "Generate a secure state value and PKCE challenge.",
                "Implement callback and token exchange handling.",
                "Implement token refresh and API integration tests."
            ],
            "human_must_do": [
                "Sign in to Linear and create the OAuth application.",
                "Choose and register the real callback URL.",
                "Review requested permissions and application details.",
                "Test using an authorized Linear workspace.",
                "Make any provider-side distribution or publishing decisions."
            ],
            "verification_notes": "Provider-specific OAuth endpoints, scopes, PKCE, callback handling and token refresh are documented by Linear. Setup time and approval wait are not specified. Gemini was unavailable; this is a source-based fallback, not an AI-generated result.",
            "sources": [
                {
                    "label": "Linear OAuth 2.0 Authentication",
                    "url": "https://linear.app/developers/oauth-2-0-authentication"
                }
            ],
            "research_mode": "Verified provider-specific fallback (Gemini unavailable)"
        }


    excerpt = source_text[:650]
    return {
        "app_name": app_name,
        "summary": f"Starter OAuth research for {app_name}, based on the submitted public documentation page. Confirm every provider-specific setting in the source before implementation.",
        "difficulty": "Unknown — verify",
        "estimated_time": "Not verified. Allow time for app configuration, testing and any provider review.",
        "approval_wait": "Not verified — depends on provider, scopes, publishing status and account type.",
        "steps": [
            {"title": "Read the provider's OAuth overview", "detail": f"Review the source page and identify the supported OAuth flow, authorization endpoint, token endpoint and prerequisites. Source excerpt: {excerpt[:260]}...", "owner": "Agent"},
            {"title": "Create or select a developer project", "detail": "Open the provider's developer console and create an app/project if required. Exact console steps were not verified by this prototype.", "owner": "Human"},
            {"title": "Configure redirect URI", "detail": "Register the exact callback URL used by your integration. It must match the URI sent in the authorization request.", "owner": "Human"},
            {"title": "Configure scopes and consent", "detail": "Request only the minimum scopes needed. Check whether sensitive/restricted scopes trigger verification or review.", "owner": "Human"},
            {"title": "Test the authorization flow", "detail": "Run an end-to-end test with a development account, verify the callback and token exchange, and handle errors securely.", "owner": "Agent"}
        ],
        "requirements": [
            "A provider developer account or workspace may be required (not verified).",
            "A public or local development callback URL appropriate to the provider.",
            "A clear list of required scopes and a privacy policy if required by the provider."
        ],
        "blockers": [
            "Provider-specific approval and verification requirements are not confirmed.",
            "Some scopes or production distribution may require a review.",
            "The submitted page may not cover every console setup step."
        ],
        "agent_can_do": [
            "Read the submitted documentation page and extract likely requirements.",
            "Draft a setup checklist and identify unknowns.",
            "Help validate redirect URI and scope configuration."
        ],
        "human_must_do": [
            "Sign in to the provider console and accept legal terms.",
            "Complete identity, organization or domain verification if requested.",
            "Submit provider review and handle any account-specific approval."
        ],
        "verification_notes": f"Source page fetched: {title}. No provider console login, OAuth app creation or approval submission was attempted. {ai_error}",
        "sources": [{"label": title, "url": url}],
        "research_mode": "Evidence-based starter guide (AI unavailable)"
    }

@app.route("/")
def index():
    return render_template("index.html", apps=APP_LIBRARY)

@app.route("/api/apps")
def apps():
    return jsonify(APP_LIBRARY)

@app.route("/api/apps/<slug>")
def app_detail(slug):
    item = next((x for x in APP_LIBRARY if x["slug"] == slug), None)
    if not item:
        abort(404)
    return jsonify(item)

@app.route("/api/generate", methods=["POST"])
def generate():
    body = request.get_json(silent=True) or {}
    app_name = (body.get("app_name") or "").strip()[:100]
    url = (body.get("url") or "").strip()
    if not app_name or not url:
        return jsonify({"error": "Enter an app name and its official OAuth documentation URL."}), 400
    try:
        title, source_text = fetch_page(url)
        guide = make_ai_guide(app_name, url, title, source_text)
        guide_id = uuid.uuid4().hex[:10]
        guide["id"] = guide_id
        guide["created_at"] = datetime.now(timezone.utc).isoformat()
        with db() as conn:
            conn.execute(
                "INSERT INTO guides (id, app_name, payload, created_at) VALUES (?, ?, ?, ?)",
                (guide_id, app_name, json.dumps(guide), guide["created_at"])
            )
        return jsonify({"guide": guide, "share_url": request.host_url.rstrip("/") + "/guide/" + guide_id})
    except requests.RequestException as exc:
        return jsonify({"error": f"Could not fetch that page: {exc.__class__.__name__}. Check the URL and try again."}), 422
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Guide generation failed")
        return jsonify({"error": "Guide generation failed. Check the server log and try again."}), 500

@app.route("/library/<slug>")
def library_guide(slug):
    item = next((x for x in APP_LIBRARY if x["slug"] == slug), None)
    if not item:
        abort(404)
    return render_template("shared.html", guide=item)

@app.route("/guide/<guide_id>")
def shared_guide(guide_id):
    with db() as conn:
        row = conn.execute("SELECT payload FROM guides WHERE id = ?", (guide_id,)).fetchone()
    if not row:
        abort(404)
    return render_template("shared.html", guide=json.loads(row["payload"]))

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

init_db()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
