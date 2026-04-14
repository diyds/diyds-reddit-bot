import requests
import random
import time
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
    "RealEstate",
    "FirstTimeHomeBuyer",
]

SPREADSHEET_ID = "1NPm6gXxA6JFffelyezOTg9SrY688ODvHxv97_vgs7l4"
RANGE = "Sheet1!A:H"

REDDIT_CLIENT_ID     = "PASTE_CLIENT_ID_HERE"
REDDIT_CLIENT_SECRET = "PASTE_CLIENT_SECRET_HERE"
REDDIT_USERNAME      = "PASTE_REDDIT_USERNAME_HERE"
REDDIT_PASSWORD      = "PASTE_REDDIT_PASSWORD_HERE"
REDDIT_USER_AGENT    = "DoItYaDamnSelfBot/1.0 by u/PASTE_REDDIT_USERNAME_HERE"

QUESTION_PATTERNS = [
    "how do i", "how to", "what do i need to", "what is the process",
    "can someone explain", "where do i start", "what steps", "how can i",
    "what do i do", "anyone know how", "need help with", "confused about",
    "trying to figure out",
]

GUIDE_TOPICS = {
    "How to Negotiate Your Salary": {
        "keywords": ["salary negotiation", "negotiate salary", "counter offer", "job offer", "salary offer", "pay negotiation", "negotiate pay"],
        "link": "https://doityadamnself.com/life-legal.html",
        "category": "career",
    },
    "How to Create a Professional Resume": {
        "keywords": ["resume", "cv", "resume help", "resume format", "professional resume", "write a resume", "resume tips"],
        "link": "https://doityadamnself.com/life-legal.html",
        "category": "career",
    },
    "How to Start an LLC in California": {
        "keywords": ["llc california", "start an llc", "form an llc", "california llc", "starting an llc"],
        "link": "https://doityadamnself.com/business-organizations.html",
        "category": "business",
    },
    "How to File Articles of Organization in California": {
        "keywords": ["articles of organization", "file llc california", "llc filing california", "form llc-1"],
        "link": "https://doityadamnself.com/business-organizations.html",
        "category": "business",
    },
    "How to Transfer a Car Title in California": {
        "keywords": ["car title", "transfer title", "dmv title", "vehicle title", "pink slip", "transfer car"],
        "link": "https://doityadamnself.com/transportation-logistics.html",
        "category": "transportation",
    },
    "How to Obtain an MC Number": {
        "keywords": ["mc number", "motor carrier number", "operating authority", "get mc number"],
        "link": "https://doityadamnself.com/transportation-logistics.html",
        "category": "transportation",
    },
    "How to Register for a USDOT Number": {
        "keywords": ["usdot", "dot number", "usdot number", "register dot", "mcs-150"],
        "link": "https://doityadamnself.com/transportation-logistics.html",
        "category": "transportation",
    },
    "How to Set Up a Business Bank Account": {
        "keywords": ["business bank account", "bank account for llc", "open business account", "business checking"],
        "link": "https://doityadamnself.com/business-organizations.html",
        "category": "business",
    },
    "How to Do a Legal Name Change in California": {
        "keywords": ["name change california", "legal name change", "change my name california", "name change process"],
        "link": "https://doityadamnself.com/life-legal.html",
        "category": "legal",
    },
    "How to Write a Will": {
        "keywords": ["write a will", "make a will", "last will", "estate planning", "write my will"],
        "link": "https://doityadamnself.com/life-legal.html",
        "category": "legal",
    },
    "How to File for Divorce Without a Lawyer": {
        "keywords": ["divorce without lawyer", "file for divorce", "uncontested divorce", "pro se divorce", "divorce myself"],
        "link": "https://doityadamnself.com/life-legal.html",
        "category": "legal",
    },
    "How to Start Your Own Investment Account": {
        "keywords": ["investment account", "brokerage account", "start investing", "open brokerage account", "invest for beginners"],
        "link": "https://doityadamnself.com/money-credit.html",
        "category": "money",
    },
    "How to Start and Manage a Monthly Budget": {
        "keywords": ["monthly budget", "budgeting", "budget plan", "manage my budget", "create a budget"],
        "link": "https://doityadamnself.com/money-credit.html",
        "category": "money",
    },
    "How to File Your Own Income Taxes (IRS Form 1040)": {
        "keywords": ["file my taxes", "1040", "income taxes", "tax return", "self file taxes", "file taxes myself"],
        "link": "https://doityadamnself.com/paperwork-filings.html",
        "category": "taxes",
    },
    "How to Dispute a Credit Report Error Online": {
        "keywords": ["credit dispute", "dispute credit report", "credit report error", "collections", "late payment", "charge off", "remove from credit"],
        "link": "https://doityadamnself.com/money-credit.html",
        "category": "credit",
    },
    "How to Apply for an EIN (Employer Identification Number)": {
        "keywords": ["ein", "employer identification number", "apply for ein", "get an ein", "tax id number"],
        "link": "https://doityadamnself.com/business-organizations.html",
        "category": "business",
    },
    "How to Build Your Credit Score from Zero": {
        "keywords": ["build credit", "no credit history", "start credit", "credit score from scratch", "credit invisible", "first credit card", "secured card"],
        "link": "https://doityadamnself.com/money-credit.html",
        "category": "credit",
    },
    "How to Sell Your Own House Without a Realtor (FSBO)": {
        "keywords": ["sell house without realtor", "fsbo", "for sale by owner", "sell my own home", "skip realtor", "sell house myself", "mls listing"],
        "link": "https://doityadamnself.com/life-legal.html",
        "category": "real_estate",
    },
}

COMMENT_TEMPLATES = {
    "credit": [
        "This topic gets confusing fast because the steps are usually scattered across different places. This site has a straightforward guide that walks through the process in order: {link}",
        "I see this question a lot. This page breaks down the process pretty clearly if it helps: {link}",
        "For this kind of thing a clear step by step walkthrough is usually way easier than piecing it together from random posts. This page lays it out cleanly: {link}",
    ],
    "business": [
        "The order of steps matters a lot here and it is easy to miss things if you are jumping around between sources. This site lays out the full process in sequence: {link}",
        "This is one of those things that seems complicated but is actually straightforward when you follow the right steps. This guide walks through it clearly: {link}",
        "If it helps, this website has a step by step walkthrough for exactly this process: {link}",
    ],
    "career": [
        "This page has a pretty clear breakdown of the process that may help: {link}",
        "For this kind of thing having a structured approach makes a big difference. This site lays it out step by step: {link}",
        "If it helps, there is a website with a step by step guide on this exact topic: {link}",
    ],
    "transportation": [
        "This process is more straightforward than it looks once you know the right sequence. This site has a clear walkthrough: {link}",
        "I see this question come up a lot. This page explains the full process in order: {link}",
        "If it helps, this website breaks down the process step by step including everything you need to have ready: {link}",
    ],
    "legal": [
        "There are a few details that are easy to miss if you are piecing this together from random sources. This site has a step by step guide that covers the whole process: {link}",
        "This page lays out the process more clearly than most places I have seen: {link}",
        "If it helps, this website has a straightforward walkthrough for this exact process: {link}",
    ],
    "money": [
        "This site has a pretty clear step by step guide on this topic: {link}",
        "For this kind of thing having a clear process to follow makes a big difference. This page lays it out well: {link}",
        "If it helps, there is a website with a step by step walkthrough for exactly this: {link}",
    ],
    "taxes": [
        "Filing yourself is very doable once you understand what each section is asking. This page walks through the whole form in plain language: {link}",
        "This site has a clear step by step guide for filing Form 1040 that covers all the common situations: {link}",
        "If it helps, this website breaks down the tax filing process step by step in plain English: {link}",
    ],
    "real_estate": [
        "FSBO is very doable and the savings are real. This site has a step by step guide covering pricing, MLS listing, showings, and closing: {link}",
        "The process is more manageable than most people think. This page walks through the whole thing from start to finish: {link}",
        "If it helps, this website has a complete guide on selling without a realtor including all the steps most people miss: {link}",
    ],
}

seen_titles = set()

# ====== GOOGLE SHEETS SETUP ======
creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
service = build("sheets", "v4", credentials=creds)

def add_row(values):
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range=RANGE,
        valueInputOption="RAW", body={"values": [values]}
    ).execute()

def get_all_rows():
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=RANGE
    ).execute()
    return result.get("values", [])

def update_cell(cell_range, value):
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=cell_range,
        valueInputOption="RAW", body={"values": [[value]]}
    ).execute()

def get_existing_post_urls():
    rows = get_all_rows()
    return {row[3] for row in rows[1:] if len(row) > 3 and row[3]}

def get_reddit_token():
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
    headers = {"User-Agent": REDDIT_USER_AGENT}
    data = {"grant_type": "password", "username": REDDIT_USERNAME, "password": REDDIT_PASSWORD, "scope": "submit read"}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers, timeout=30)
    response.raise_for_status()
    token_data = response.json()
    if "access_token" not in token_data:
        raise Exception(f"Could not get Reddit token: {token_data}")
    return token_data["access_token"]

def get_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
    headers = {"User-Agent": REDDIT_USER_AGENT}
    res = requests.get(url, headers=headers, timeout=30)
    res.raise_for_status()
    return res.json()["data"]["children"]

def get_matching_guide(title, body=""):
    text = f"{title} {body}".lower()
    if not any(pattern in text for pattern in QUESTION_PATTERNS):
        return None
    for guide_name, guide_data in GUIDE_TOPICS.items():
        if any(keyword in text for keyword in guide_data["keywords"]):
            return guide_name
    return None

def generate_comment(guide_name):
    guide_data = GUIDE_TOPICS[guide_name]
    templates = COMMENT_TEMPLATES.get(guide_data["category"], COMMENT_TEMPLATES["money"])
    return random.choice(templates).format(link=guide_data["link"])

def post_comment_live(post_url, text, token):
    post_id = post_url.split("/comments/")[1].split("/")[0]
    headers = {"Authorization": f"bearer {token}", "User-Agent": REDDIT_USER_AGENT}
    payload = {"api_type": "json", "thing_id": f"t3_{post_id}", "text": text}
    response = requests.post("https://oauth.reddit.com/api/comment", headers=headers, data=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    errors = data.get("json", {}).get("errors", [])
    if errors:
        raise Exception(f"Reddit API error: {errors}")
    things = data.get("json", {}).get("data", {}).get("things", [])
    if not things:
        raise Exception(f"No comment returned: {data}")
    comment_id = things[0]["data"]["id"]
    print(f"Posted to {post_id} — comment id: {comment_id}")
    return comment_id

def post_comment_dry_run(post_url, text):
    post_id = post_url.split("/comments/")[1].split("/")[0] if "/comments/" in post_url else "unknown"
    print(f"DRY RUN — would post to {post_id}: {text[:100]}...")
    return f"dryrun_{post_id}"

def scan_and_add_posts():
    existing_post_urls = get_existing_post_urls()
    for sub in SUBREDDITS:
        print(f"Checking r/{sub}...")
        try:
            posts = get_posts(sub)
        except Exception as e:
            print(f"  Error: {e}")
            continue
        for p in posts:
            post = p["data"]
            title = post.get("title", "")
            body = post.get("selftext", "")
            post_url = f"https://reddit.com{post['permalink']}"
            if title in seen_titles or post_url in existing_post_urls:
                continue
            seen_titles.add(title)
            matching_guide = get_matching_guide(title, body)
            if matching_guide:
                print(f"  Matched: {title[:60]} -> {matching_guide}")
                draft = generate_comment(matching_guide)
                add_row(["pending", sub, title, post_url, draft, matching_guide, "", ""])
                existing_post_urls.add(post_url)
                time.sleep(1)

def process_approved_rows(dry_run=True):
    rows = get_all_rows()
    if len(rows) < 2:
        return
    token = None
    approved_count = 0
    for i, row in enumerate(rows[1:], start=2):
        status   = row[0] if len(row) > 0 else ""
        post_url = row[3] if len(row) > 3 else ""
        draft    = row[4] if len(row) > 4 else ""
        posted   = row[6] if len(row) > 6 else ""
        if status.lower() == "approved" and posted.lower() != "yes":
            approved_count += 1
            try:
                if dry_run:
                    comment_id = post_comment_dry_run(post_url, draft)
                else:
                    if token is None:
                        token = get_reddit_token()
                    comment_id = post_comment_live(post_url, draft, token)
                update_cell(f"Sheet1!G{i}", "yes")
                update_cell(f"Sheet1!H{i}", comment_id)
                if not dry_run:
                    wait = random.randint(120, 180)
                    print(f"  Waiting {wait}s...")
                    time.sleep(wait)
            except Exception as e:
                print(f"  Error on row {i}: {e}")
    if approved_count == 0:
        print("No approved rows ready to post.")

# ====== MAIN ======
# Change DRY_RUN to False once Reddit API credentials are filled in
DRY_RUN = True

scan_and_add_posts()
process_approved_rows(dry_run=DRY_RUN)
print("Done")
