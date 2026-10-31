"""Rules -> a trained domain -> an application that can ask for decisions. Run once."""
import json, os, time
from earl_sdk import EarlClient
from earl_sdk.domains import DomainTrainer
from host import URL, session_token

developer = EarlClient(URL, session_token())

trained = DomainTrainer(developer, log=print).train_directory(
    "domain", name=f"Journal-entry rules {time.strftime('%Y%m%d-%H%M%S')}", description="Northwind approval policy",
    foundational_kb_package_id=int(os.environ.get("EARL_KB_PACKAGE", "1")),
    earl_engine_id=int(os.environ["EARL_ENGINE_ID"]) if os.environ.get("EARL_ENGINE_ID") else None)

app = developer.create_application("Journal-entry review", "Governed journal-entry approval")
api_key = app.create_credential("build")["api_key"]
app.connect_domain(trained["domain_id"])
workflow = app.bind_workflow()

with open(".earl.json", "w") as f:
    json.dump({"url": URL, "api_key": api_key, "workflow": workflow.id, "domain": trained["domain_id"]}, f)
print("ready: workflow", workflow.id)
