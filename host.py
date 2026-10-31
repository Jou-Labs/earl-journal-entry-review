"""The host: what your system knows about an entry, as a claim and an action. EARL decides; your system acts."""
import json, os
from earl_sdk import EarlClient

URL = os.environ.get("EARL_URL", "https://platform.jou-labs.com")


def session_token():
    """Your session, saved by sign_in.py. It builds; the application's own key runs."""
    return os.environ.get("EARL_TOKEN") or open(".session-token").read().strip()


def workflow():
    c = json.load(open(".earl.json"))
    client = EarlClient(c["url"], c["api_key"])
    return client, client.workflow(c["workflow"])


def claim(entry):
    a = lambda w: "an" if w[0] in "aeiou" else "a"
    return f"{a(entry['type']).capitalize()} {entry['type']} entry requires {a(entry['route'])} {entry['route']} approval."


def action(entry):
    return entry.get("action", "post_entry")


def decide(wf, entry):
    return wf.decide(claim(entry), action(entry), actor=entry["actor"], idempotent=False)


def show(entry, d):
    r = d.result or {}
    print(f"{entry['id']}  {r.get('decision', d.outcome_class):6}  {claim(entry)}  {action(entry)} by {entry['actor']}")
    for reason in r.get("reasons") or []:
        print("          ", reason)
