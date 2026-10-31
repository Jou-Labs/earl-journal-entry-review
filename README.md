# Governed journal-entry review with EARL

A small application that decides whether a journal entry may post. The rules are written down, each decision names the
rule behind it, and each decision leaves a signed record you can check without trusting the platform.

Northwind Manufacturing is invented. So are its ledger and its approvers.

**The pattern:** Rules, evidence, decision, release or refusal, record, verification.

## What you need

- Python 3.11 or later
- An account on `platform.jou-labs.com`. To request access, use **Request a Platform Briefing** at the very bottom of the
  [platform page](https://www.jou-labs.com/platform).

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
curl -o earl-sdk.tar.gz https://platform.jou-labs.com/api/docs/sdk
tar xzf earl-sdk.tar.gz
pip install "./earl-sdk/python[crypto]"

python sign_in.py    # saves a one-hour token to .session-token; your password stays with you
python build.py      # trains the rules and creates your application, once
python review.py     # five entries, three outcomes
python break_it.py   # tries to get past the rules
python verify.py     # checks the records, then tampers with one
```

Delete `.session-token` when you finish. `build.py` writes `.earl.json`, which holds your application's API key. Both are
in `.gitignore`. Keep them out of anything you share.

## What you should see

`review.py`:

```text
JE-1001  ALLOW   A manual entry requires a controller approval.  post_entry by controller
JE-1002  ALLOW   An accrual entry requires a controller approval.  post_entry by controller
JE-1003  DENY    A recurring entry requires a controller approval.  post_entry by controller
JE-1004  DENY    A reversal entry requires a controller approval.  post_entry by controller
JE-1005  REVIEW  A manual entry requires a controller approval.  void_entry by controller
```

Each DENY and REVIEW also prints its reasons. `verify.py` ends like this:

```text
  record.json: exit 0  VERIFIED
change DENY to ALLOW in the record:
  tampered.json: exit 2  NOT VERIFIED
then sign it again with a key of your own:
  forged.json: exit 2  NOT VERIFIED
```

## What is in here

| Path | What it is |
| --- | --- |
| `domain/corpus/` | Northwind's rules, in plain sentences |
| `domain/vocabulary.py`, `domain/curriculum.json` | The words the domain reasons with, and the lessons that teach them |
| `domain/policy.json` | What to do with the evidence, and who may take which action |
| `build.py` | Trains the domain and creates the application |
| `host.py` | Your side: turns an entry into a claim and an action, and asks for a decision |
| `review.py` | Decides five entries |
| `break_it.py` | Changes one thing at a time, then tries to rewrite the rules |
| `verify.py` | Checks records with the SDK and with a verifier that shares no code with it |
| `independent_verifier.py` | The standalone verifier |

## What this does and does not show

- **EARL decides; your system acts.** Records say `mode: advisory` and `enforced: false`. `review.py` marks where your
  system would post an entry.
- **`actor` is what your system reports.** EARL applies the rule to it. Proving who the person is stays with your system.
- **A valid signature proves a record is intact and who issued it.** It does not prove the verdict is true.
- **Pin the issuer's key.** A record carries its own key, so without a saved key, a record altered and re-signed with
  another key still passes. `verify.py` saves the key on first use and checks everything against that copy. That first
  use is the moment you trust the platform, so compare it with a copy you hold elsewhere if you can.
- **Records are signed one at a time.** Each has a sequence number, but none links to the one before it.

## License

MIT. See [LICENSE](LICENSE).
