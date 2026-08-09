"""
NEA checklist categories used as the grounding ruleset for KopiCheck.

These categories are drawn from NEA's published self checklist for food
establishments (nea.gov.sg), covering the hygiene and maintenance
requirements most relevant to day to day stall operation. This is not
the full pre licensing checklist. It is the subset that is realistically
observable during live service through a camera and microphone, which
is what a passive agent can actually verify.
"""

CHECKLIST_CATEGORIES = {
    "temperature": {
        "label": "Temperature",
        "description": (
            "Refrigerator and chiller temperature gauges checked at "
            "scheduled intervals. NEA requires temperature gauges to be "
            "installed on all refrigerators and chillers."
        ),
        "check_interval_minutes": 180,
        "safe_range_celsius": (0, 8),
    },
    "cleaning": {
        "label": "Cleaning",
        "description": (
            "Cleaning schedule adherence, including prep table sanitising, "
            "equipment cleaning, and closing sanitisation."
        ),
        "check_interval_minutes": None,  # event driven, not schedule driven
    },
    "cross_contamination": {
        "label": "Cross Contamination",
        "description": (
            "Raw and cooked or ready to eat food kept separate. Includes "
            "cutting board reuse, storage proximity, and uncovered "
            "ready to eat food not protected by sneeze guards."
        ),
        "check_interval_minutes": None,
    },
    "pest_control": {
        "label": "Pest Control",
        "description": (
            "Visible signs of pest activity, and confirmation that pest "
            "control measures (bins covered, food stored off floor) are "
            "in place."
        ),
        "check_interval_minutes": None,
    },
    "hygiene_certification": {
        "label": "Hygiene Certification",
        "description": (
            "Food handler hygiene practices, such as handwashing before "
            "handling ready to eat food and use of gloves where required."
        ),
        "check_interval_minutes": None,
    },
}

# Detected event severity, used by the orchestration layer to decide
# whether to log silently, nudge the owner, or escalate for human
# confirmation before it is treated as fact.
SEVERITY = {
    "ok": "Logged automatically, no action needed.",
    "reminder": "Owner is nudged to complete a scheduled check.",
    "flagged": "Event is queued for human confirmation before being logged.",
}
