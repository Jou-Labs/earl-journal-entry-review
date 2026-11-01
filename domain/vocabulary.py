"""The words this domain reasons with, grouped by what they belong to. Nouns only."""

CLUSTERS = [
    ("entry_types", "entry", ["entry", "manual", "treasury", "recurring", "accrual", "reversal", "suspense", "cash", "revenue"]),
    ("approvers", "approval", ["approver", "preparer", "controller", "treasurer", "approval", "signature"]),
    ("accounts", "account", ["account", "ledger", "revenue", "expense", "cash", "suspense"]),
    ("exceptions", "exception", ["exception", "flag", "reconciliation", "close", "narrative", "schedule"]),
    ("manual_entry", "manual", ["manual", "controller", "preparer", "narrative"]),
    ("treasury_entry", "treasury", ["treasury", "treasurer", "controller", "preparer", "cash", "revenue"]),
    ("accrual_entry", "accrual", ["accrual", "controller", "narrative", "expense"]),
    ("reversal_entry", "reversal", ["reversal", "preparer", "accrual"]),
    ("recurring_entry", "recurring", ["recurring", "schedule"]),
    ("suspense_entry", "suspense", ["suspense", "reconciliation", "exception"]),
]

ALIASES = {
    "controller": ["financial controller"],
}


def anchor_chain():
    return [("entry", "approval"), ("approval", "account"), ("account", "exception")]
