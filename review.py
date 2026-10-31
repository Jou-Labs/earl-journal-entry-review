"""Evidence -> decision -> release or refusal -> record."""
import json
from host import decide, show, workflow

client, wf = workflow()
for entry in json.load(open("entries.json")):
    d = decide(wf, entry)
    show(entry, d)
    if d.result.get("decision") == "ALLOW":
        pass  # your system posts the entry here; nothing else ever does
    elif d.result.get("decision") == "REVIEW":
        pass  # your system sends it to a person
