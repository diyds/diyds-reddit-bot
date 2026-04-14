import requests
import random
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ====== CONFIG ======
SUBREDDITS = [
    "credit",
    "personalfinance",
    "smallbusiness",
    "Entrepreneur",
    "startups",
    "resumes",
    "jobs",
    "careerguidance",
    "Truckers",
    "OwnerOperators",
    "legaladvice",
    "California",
]

SPREADSHEET_ID = "1NPm6gXxA6JFffelyezOTg9SrY688ODvHxv97_vgs7l4"
RANGE = "Sheet1!A:H"

QUESTION_PATTERNS = [
    "how do i",
    "how to",
    "what do i need to",
    "what is the process",
    "can someone explain",
    "where do i start",
    "what steps",
    "how can i",
    "what do i do",
]

GUIDE_TOPICS = {
    "How to Negotiate Your Salary": [
        "salary negotiation",
        "negotiate salary",
        "counter offer",
        "job offer",
        "salary offer",
        "pay negotiation",
    ],
    "How to Create a Professional Resume": [
        "resume",
        "cv",
        "resume help",
        "resume format",
        "professional resume",
    ],
    "How to Start an LLC in California": [
        "llc california",
        "start an llc",
        "form an llc",
        "california llc",
    ],
    "How to File Articles of Organization in California": [
        "articles of organization",
        "file llc california",
        "llc filing california",
    ],
    "How to Transfer a Car Title in California": [
        "car title",
        "transfer title",
        "dmv title",
        "vehicle title",
        "pink slip",
    ],
    "How to Obtain an MC Number": [
        "mc number",
        "motor carrier number",
        "operating authority",
    ],
    "How to Register for a USDOT Number": [
        "usdot",
        "dot number",
        "usdot number",
    ],
    "How to Set Up a Business Bank Account": [
        "business bank account",
        "bank account for llc",
        "open business account",
    ],
    "How to Do a Legal Name Change in California": [
        "name change california",
        "legal name change",
        "change my name california",
    ],
    "How to Write a Will": [
        "write a will",
        "make a will",
        "last will",
        "estate planning",
    ],
    "How to File for Divorce Without a Lawyer": [
        "divorce without lawyer",
        "file for divorce",
        "uncontested divorce",
        "pro se divorce",
    ],
    "How to Start Your Own Investment Account": [
        "investment account",
        "brokerage account",
        "start investing",
        "open brokerage account",
    ],
    "How to Start and Manage a Monthly Budget": [
        "monthly budget",
        "budgeting",
        "budget plan",
        "manage my budget",
    ],
    "How to File Your Own Income Taxes (Form 1040)": [
        "file my taxes",
        "1040",
        "income taxes",
        "tax return",
        "self file taxes",
    ],
    "How to Dispute a Credit Report Error Online": [
        "credit dispute",
        "dispute credit report",
        "credit report error",
        "collections",
        "late payment",
        "charge off",
    ],
    "How to Apply for an EIN (Employer Identification Number)": [
        "ein",
        "employer identification number",
        "apply for ein",
        "get an ein",
    ],
}

seen_titles = set()

# ====== GOOGLE SHEETS SETUP ======
creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service = build("sheets", "v4", credentials=creds)

# ====== SHEETS HELPERS ======
def add_row(values):
    body = {"values": [values]}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE,
        valueInputOption="RAW",
        body=body
    ).execute()

def get_all_rows():
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()
    return result.get("values", [])

def update_cell(cell_range, value):
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=cell_range,
        valueInputOption="RAW",
        body={"values": [[value]]}
    ).execute()

def get_existing_post_urls():
    rows = get_all_rows()
    existing_urls = set()

    for row in rows[1:]:
        if len(row) > 3 and row[3]:
            existing_urls.add(row[3])

    return existing_urls

# ====== GET REDDIT POSTS ======
def get_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=15"
    headers = {"User-Agent": "simple-script"}
    res = requests.get(url, headers=headers, timeout=30)
    res.raise_for_status()
    data = res.json()
    return data["data"]["children"]

# ====== MATCH LOGIC ======
def get_matching_guide(title, body=""):
    text = f"{title} {body}".lower()

    is_question = any(pattern in text for pattern in QUESTION_PATTERNS)
    if not is_question:
        return None

    for guide_name, keywords in GUIDE_TOPICS.items():
        if any(keyword in text for keyword in keywords):
            return guide_name

    return None

# ====== COMMENT GENERATOR ======
def generate_comment(title, guide_name):
    t = title.lower()

    if "credit" in t or "dispute" in t or "collections" in t:
        options = [
            "I ran into something similar and what helped me most was slowing down and handling each part separately instead of treating it like one simple form.",
            "I went through this before and the biggest difference was being more specific about the issue and keeping track of everything I submitted.",
        ]
        return random.choice(options)

    if "llc" in t or "ein" in t or "articles of organization" in t or "business bank" in t:
        options = [
            "I remember this being confusing at first because everything seemed out of order. Once I followed the right sequence it made a lot more sense.",
            "What helped me most was figuring out the exact order of steps first, that made the whole thing feel a lot easier.",
        ]
        return random.choice(options)

    if "resume" in t or "salary" in t or "job" in t:
        options = [
            "I dealt with something similar and what helped was making the process more structured instead of trying to guess my way through it.",
            "I went through this too and it got easier once I broke it into clear steps and focused on the parts that actually mattered.",
        ]
        return random.choice(options)

    if "usdot" in t or "mc number" in t:
        options = [
            "I remember this being more confusing than it should have been. What helped me was following the steps in the right order instead of piecing it together from different places.",
            "I looked into this before and the biggest help was just having a clear sequence to follow because the process can feel more complicated than it really is.",
        ]
        return random.choice(options)

    if "divorce" in t or "will" in t or "name change" in t:
        options = [
            "I looked into this and what helped most was going step by step because there are a few details that are easy to miss if you jump around.",
            "What made the difference for me was following a more structured process instead of trying to figure it out from random pages.",
        ]
        return random.choice(options)

    return "I went through something similar and what helped me most was following a more structured step by step approach instead of piecing everything together from random places."

# ====== DRY RUN POST FUNCTION ======
def post_comment(post_url, text):
    try:
        post_id = post_url.split("/comments/")[1].split("/")[0]
    except Exception:
        post_id = "unknown"

    print(f"Would post to {post_id}: {text[:80]}...")
    return f"dryrun_{post_id}"

# ====== SCAN REDDIT AND ADD MATCHES TO SHEET ======
def scan_and_add_posts():
    existing_post_urls = get_existing_post_urls()

    for sub in SUBREDDITS:
        print("Checking subreddit:", sub)
        posts = get_posts(sub)

        for p in posts:
            post = p["data"]
            title = post.get("title", "")
            body = post.get("selftext", "")
            post_url = f"https://reddit.com{post['permalink']}"

            if title in seen_titles:
                continue
            seen_titles.add(title)

            if post_url in existing_post_urls:
                continue

            matching_guide = get_matching_guide(title, body)

            if matching_guide:
                print("Matched:", title, "->", matching_guide)

                draft = generate_comment(title, matching_guide)

                add_row([
                    "pending",
                    sub,
                    title,
                    post_url,
                    draft,
                    matching_guide,
                    "",
                    ""
                ])

                existing_post_urls.add(post_url)

# ====== PROCESS APPROVED ROWS ======
def process_approved_rows():
    rows = get_all_rows()

    if len(rows) < 2:
        return

    for i, row in enumerate(rows[1:], start=2):
        status = row[0] if len(row) > 0 else ""
        post_url = row[3] if len(row) > 3 else ""
        draft_comment = row[4] if len(row) > 4 else ""
        posted = row[6] if len(row) > 6 else ""

        if status.lower() == "approved" and posted.lower() != "yes":
            comment_id = post_comment(post_url, draft_comment)
            update_cell(f"Sheet1!G{i}", "yes")
            update_cell(f"Sheet1!H{i}", comment_id)

# ====== MAIN ======
scan_and_add_posts()
process_approved_rows()
print("Done")