"""Try to get an entry through. Every attempt starts from one that passes, with one thing wrong."""
import copy, json, os
from earl_sdk import EarlApiError, EarlClient
from earl_sdk.domains import DomainTrainer
from host import decide, session_token, show, workflow

client, wf = workflow()
good = {"id": "JE-2000", "type": "manual", "route": "controller", "actor": "controller"}
attempts = {
    "the control: a good entry": good,
    "no authority: the preparer posts their own entry": {**good, "actor": "preparer"},
    "no actor at all": {**good, "actor": None},
    "a route the policy forbids": {**good, "type": "recurring"},
    "a rule that was never written": {**good, "route": "auditor"},
}
for name, entry in attempts.items():
    print("---", name)
    show(entry, decide(wf, entry))


def attempt(name, call):
    print("---", name)
    try:
        d = call()
        print(f"  {(d.result or {}).get('decision', d.outcome_class)}", (d.result or {}).get("reasons"))
    except EarlApiError as e:
        print(f"  refused: HTTP {e.status}", str(e.detail)[:120])


attempt("no evidence: an empty claim", lambda: wf.decide("", "post_entry", actor="controller", idempotent=False))
attempt("conflicting evidence: one good claim, one the policy forbids", lambda: wf.decide(
    "A manual entry requires a controller approval. A recurring entry requires a controller approval.",
    "post_entry", actor="controller", idempotent=False))
attempt("a second clause inside one sentence", lambda: wf.decide(
    "A manual entry requires a controller approval and a recurring entry requires a controller approval.",
    "post_entry", actor="controller", idempotent=False))
attempt("an action no rule covers", lambda: wf.decide("A manual entry requires a controller approval.", "delete_ledger", actor="controller", idempotent=False))

config = json.load(open(".earl.json"))
policy = json.load(open("domain/policy.json"))
print("--- the application rewrites its own rules, with its own key")
weak = copy.deepcopy(policy)
weak["dispositions"]["CONTESTED"] = "ALLOW"
try:
    DomainTrainer(client).set_policy(config["domain"], weak)
    print("  ACCEPTED: the application changed its rules")
except EarlApiError as e:
    print(f"  refused: HTTP {e.status}", str(e.detail)[:120])

print("--- an invalid rule, from the developer")
bad = copy.deepcopy(policy)
bad["rules"].append({"id": "x", "type": "allow_everything", "action": "allow"})
try:
    DomainTrainer(EarlClient(config["url"], session_token())).set_policy(config["domain"], bad)
    print("  ACCEPTED: an invalid rule")
except EarlApiError as e:
    print(f"  refused: HTTP {e.status}", str(e.detail)[:160])

live = client.request("GET", f"/domains/{config['domain']}/policy")
print(f"--- the rules now: version {live['version']}, {live['policy_hash'][:16]}")
