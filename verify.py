"""Record -> verification, with a verifier that shares no code with the platform or the SDK."""
import copy, hashlib, json, os, subprocess, sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from host import workflow

client, wf = workflow()
records = wf.records()

# A record carries its issuer's key, and that alone proves nothing: anyone can sign with a key of their own and put it
# in the record. Save the issuer's key once, and check every record against the saved copy.
KEY = "issuer-public-key.txt"
if not os.path.exists(KEY):
    open(KEY, "w").write(client.issuer_public_key())
issuer = open(KEY).read().strip()
print(f"{sum(client.verify_offline(r, pin_public_key=issuer)['valid'] for r in records)} of {len(records)} records verify through the SDK")

denied = next(r.record for r in records if (r.record["result"] or {}).get("decision") == "DENY")
print(f"record {denied['sequence']}: {denied['request']['candidate_text']}  ->  {denied['result']['decision']}")


def independent(record, name):
    json.dump(record, open(name, "w"))
    done = subprocess.run([sys.executable, "independent_verifier.py", name, "--expect-key", issuer], capture_output=True, text=True)
    print(f"  {name}: exit {done.returncode}  {done.stdout.strip().splitlines()[-1] if done.stdout.strip() else done.stderr.strip()[-90:]}")


independent(denied["signed_record"], "record.json")

tampered = copy.deepcopy(denied["signed_record"])
tampered["result"]["decision"] = "ALLOW"
print("change DENY to ALLOW in the record:")
independent(tampered, "tampered.json")

forged = copy.deepcopy(tampered)
key = Ed25519PrivateKey.generate()
raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
forged["issuer"].update(public_key=raw.hex(), key_id=hashlib.sha256(raw).hexdigest())
payload = json.dumps({k: v for k, v in forged.items() if k != "signature"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
forged["signature"].update(payload_sha256=hashlib.sha256(payload).hexdigest(), value=key.sign(payload).hex())
print("then sign it again with a key of your own:")
independent(forged, "forged.json")
