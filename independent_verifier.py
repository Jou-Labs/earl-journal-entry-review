#!/usr/bin/env python3
"""Verify an EARL signed workflow record OFFLINE, independently of the platform.

This script deliberately imports nothing from the platform: it re-derives the canonical payload itself and
checks the Ed25519 signature with the public key carried in the record. A reader who never talks to the
platform (and does not trust it) can run this.

Pass --expect-key with the issuer's key, saved out of band. Without it, only the key the record carries is
checked, so a record altered and re-signed with another key still passes.

    python independent_verifier.py record.json [--expect-key <hex raw ed25519 public key>]

Exit 0 = signature valid. Non-zero = not verified. A valid signature establishes integrity and attribution
(this record was issued by the holder of that key and has not been altered) — it does NOT establish that any
verdict inside the record is true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonical_bytes(value: Any) -> bytes:
    # Must match the issuer's canonicalization exactly: sorted keys, no whitespace, unicode preserved.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify(record: dict[str, Any], expect_key_hex: str | None = None) -> tuple[bool, list[str]]:
    notes: list[str] = []
    ok = True

    signature = record.get("signature")
    issuer = record.get("issuer")
    if not isinstance(signature, dict) or not isinstance(issuer, dict):
        return False, ["record has no signature/issuer block"]

    if signature.get("algorithm") != "Ed25519":
        return False, [f"unexpected algorithm: {signature.get('algorithm')!r}"]

    pub_hex = str(issuer.get("public_key") or "")
    try:
        pub_raw = bytes.fromhex(pub_hex)
        pub = Ed25519PublicKey.from_public_bytes(pub_raw)
    except Exception as exc:  # noqa: BLE001
        return False, [f"issuer public key unusable: {exc}"]

    # the key_id must be the sha256 of the raw public key (so a swapped key is visible)
    key_id = str(issuer.get("key_id") or "")
    computed_key_id = hashlib.sha256(pub_raw).hexdigest()
    if key_id != computed_key_id:
        ok = False
        notes.append(f"key_id mismatch: record says {key_id[:16]}…, key hashes to {computed_key_id[:16]}…")
    else:
        notes.append(f"key_id matches the public key ({key_id[:16]}…)")

    if expect_key_hex:
        if pub_hex.lower() != expect_key_hex.lower():
            ok = False
            notes.append("issuer public key does NOT match the pinned key")
        else:
            notes.append("issuer public key matches the pinned key")

    payload = canonical_bytes({k: v for k, v in record.items() if k != "signature"})
    digest = hashlib.sha256(payload).hexdigest()
    if signature.get("payload_sha256") != digest:
        ok = False
        notes.append(f"payload_sha256 mismatch: record says {signature.get('payload_sha256', '')[:16]}…, "
                     f"recomputed {digest[:16]}… (the record was altered after signing)")
    else:
        notes.append(f"payload digest matches ({digest[:16]}…)")

    try:
        pub.verify(bytes.fromhex(str(signature.get("value") or "")), payload)
        notes.append("Ed25519 signature VALID over the recomputed payload")
    except (InvalidSignature, ValueError) as exc:
        ok = False
        notes.append(f"signature INVALID: {exc or 'does not verify'}")

    return ok, notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("record", help="path to the exported signed record JSON")
    ap.add_argument("--expect-key", dest="expect_key", default=None, help="pin the issuer's raw ed25519 public key (hex)")
    args = ap.parse_args()

    record = json.loads(open(args.record, encoding="utf-8").read())
    ok, notes = verify(record, args.expect_key)
    print(f"record_id : {record.get('record_id')}")
    print(f"operation : {record.get('operation')}  (workflow {record.get('workflow_id')}, seq {record.get('sequence')})")
    for n in notes:
        print(f"  - {n}")
    print("VERIFIED" if ok else "NOT VERIFIED")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
