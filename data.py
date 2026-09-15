"""
data.py — Expanded Niche, buyer, format libraries, weird reframes, and failure risk models.
"""

PROBLEMS = [
    # Psychological & Life Transition
    ("mortality awareness", "people know time is finite but rarely translate that fact into daily decisions"),
    ("regret avoidance", "people fear reaching a milestone and realizing they postponed what truly mattered"),
    ("time blindness", "people underestimate how quickly recurring weeks, weekends, and seasons disappear"),
    ("identity transition", "a major life change leaves someone without a clear daily routine or sense of self"),
    ("future-self disconnect", "people make choices for today's comfort that their future self will regret"),
    ("social-expectation pressure", "people spend time or money following expectations they do not actually value"),
    ("existential dread", "overwhelmed by macro-level uncertainty and seeking micro-level personal agency"),
    ("burnout recovery", "rebuilding energy, boundaries, and priorities after physical and mental exhaustion"),
    ("quarter-life crisis", "feeling stuck or lost between initial career paths and personal desires"),
    ("empty nest adjustment", "redefining purpose and daily life after children leave home"),

    # Relationships & Family
    ("awkward conversations", "families avoid important conversations because they do not know how to start"),
    ("relationship drift", "close relationships weaken because nobody deliberately protects shared time"),
    ("caregiving uncertainty", "families need to coordinate care responsibilities before a crisis hits"),
    ("digital disconnect", "families spend physical time together but remain isolated on separate devices"),
    ("co-parenting friction", "separated or divorced parents struggle with clear, neutral logistics and communication"),
    ("long-distance strain", "partners or friends struggle to maintain intimacy across time zones"),
    ("legacy preservation", "grandparents and elders have stories that will be lost without structured capturing"),

    # Life Admin & Organization
    ("hidden household risk", "important information is scattered until a stressful emergency happens"),
    ("digital clutter", "people accumulate thousands of files, photos, and bookmarks with no retrieval system"),
    ("life-admin overload", "small recurring administrative tasks become chaotic when life gets busy"),
    ("financial avoidance", "people postpone small money decisions because the emotional cost feels high"),
    ("decision paralysis", "too many options or high stakes cause people to delay critical choices"),
    ("emergency preparedness", "people want to be prepared for disasters but do not know what data to organize"),
    ("relocation chaos", "moving houses or countries creates overwhelming logistical and paperwork tracking"),
    ("vehicle & home maintenance debt", "neglecting routine property maintenance until costly repairs occur"),

    # Productivity & Creative Execution
    ("creative block", "creators struggle to convert raw ideation into consistent publishing outputs"),
    ("project abandonment", "starting dozens of ambitious side projects but finishing none"),
    ("skill-gap anxiety", "feeling underqualified for new roles or tools and lacking a structured study system"),
    ("solopreneur operational fatigue", "single-person businesses drowning in manual client onboarding and admin"),
    ("habit decay", "starting strong with new habits but dropping them as soon as routine changes")
]

BUYERS = [
    # Life Stages & Demographics
    ("adult children and aging parents", "want to use limited family time intentionally and capture legacy"),
    ("couples preparing for marriage", "want shared systems for finances, goals, and lifestyle alignment"),
    ("new homeowners", "face unfamiliar recurring maintenance decisions, budgets, and document storage"),
    ("new parents", "want to preserve early childhood memories while reducing mental load and chaos"),
    ("people approaching 30", "are reassessing direction, career trajectory, money, and primary relationships"),
    ("people approaching 40", "start thinking more seriously about opportunity cost, health, and work-life balance"),
    ("people approaching 50", "feel increasing urgency around time allocation, health, and mid-life legacy"),
    ("retirees & pre-retirees", "face a large block of newly unstructured time and loss of workplace identity"),
    ("caregivers of elderly relatives", "need simple coordination, medical tracking, and legal info systems"),

    # Career & Ambition
    ("busy corporate professionals", "have high disposable income, limited time, and pay for extreme convenience"),
    ("freelancers & agency owners", "need lightweight client management, proposal, and invoicing workflows"),
    ("etsy & digital product sellers", "looking for business trackers, listing templates, and SEO tools"),
    ("content creators & podcasters", "need editorial calendars, content repurposing pipelines, and brand kit hubs"),
    ("grad students & researchers", "struggling with citation tracking, thesis planning, and deep work scheduling"),

    # Lifestyle & Mindset
    ("self-improvement enthusiasts", "already actively buy journals, planners, habit trackers, and reflection tools"),
    ("minimalists & declutterers", "want lightweight, digital-only systems that reduce physical inventory"),
    ("people moving abroad / expats", "face major legal, financial, administrative, and identity transitions"),
    ("neurodivergent adults (ADHD/Autism)", "need low-friction, visual, dopamine-friendly task systems"),
    ("budgeters & debt-free seekers", "obsessed with zero-based budgeting, payoff trackers, and financial visualizers")
]

FORMATS = [
    # Interactive & Automated Spreadsheets (High Value)
    ("interactive Google Sheets dashboard", 1.40),
    ("automated Excel budget & forecast tool", 1.35),
    ("smart dynamic tracking system", 1.30),
    ("visual habit & goal analytics spreadsheet", 1.25),

    # Notion & Workspace Systems
    ("Notion All-in-One Life Operating System", 1.35),
    ("Notion Client & Project Hub", 1.30),
    ("Notion Minimalist Second Brain Workspace", 1.25),

    # Digital & Printable Workbooks/Journals
    ("interactive iPad / GoodNotes digital planner", 1.20),
    ("fillable PDF decision workbook", 1.15),
    ("guided reflection journal (Printable & Digital)", 1.00),
    ("family conversation & card kit", 1.25),

    # Administrative & SOP Bundles
    ("complete operational SOP template suite", 1.20),
    ("emergency binder & document Vault PDF kit", 1.25),
    ("plug-and-play Canva graphics & doc bundle", 1.10),
    ("step-by-step checklist & audit system", 1.05)
]

WEIRD_REFRAMES = {
    "mortality awareness": [
        "If You Knew Your Death Date...",
        "The 4,000 Weeks Life Audit",
        "How Many Sundays Do You Have Left With Your Parents?",
        "The Final Horizon Time Design"
    ],
    "identity transition": [
        "What Will I Do With 2,000 Empty Mondays?",
        "Post-Retirement Identity & Time Design",
        "Who Am I When the Job Title Stops?",
        "The Identity Offboarding Protocol"
    ],
    "financial avoidance": [
        "The 'Stop Pretending Everything Is Fine' Money Audit",
        "Financial Anxiety De-escalation Protocol",
        "Quiet Money Dashboard for Non-Finance Brains",
        "The Anti-Budget Income Allocation Kit"
    ],
    "time blindness": [
        "Visualizing Your Life in 52-Week Blocks",
        "Where Did the Year Go? Time Leak Audit",
        "The Season Design Workbook"
    ],
    "hidden household risk": [
        "In Case I Go Missing / Unexpected Emergency Vault",
        "The 'If Anything Happens to Me' Family Binder",
        "The Chaos-Proof Household Operations Manual"
    ],
    "relationship drift": [
        "The Intimacy & Shared Goal Calibration Protocol",
        "100 Uncomfortable Questions for Long-Term Couples",
        "Friendship Audit & Time Protection Guide"
    ]
}

RISK_PATTERNS = [
    {
        "type": "Potential Weakness",
        "text": "People may find this concept fascinating intellectually but hesitate to spend real money on a digital solution."
    },
    {
        "type": "Demand Risk",
        "text": "Search intent may be strictly informational (seeking articles/advice) rather than transactional (looking for a practical buying tool)."
    },
    {
        "type": "Competition Risk",
        "text": "Existing free tools (standard Google Calendar/Excel templates) may satisfy the need despite lacking your unique positioning."
    },
    {
        "type": "Fulfillment Burden",
        "text": "Customers may expect ongoing personal support or complex customization for what should be a low-friction digital download."
    },
    {
        "type": "Platform Risk",
        "text": "The underlying platform (e.g., Notion or GoodNotes) may release native updates that make standalone templates redundant."
    },
    {
        "type": "Low Retention / LTV",
        "text": "This solves a one-time crisis or event; customers have no natural reason to buy upsells or cross-family products."
    }
]
