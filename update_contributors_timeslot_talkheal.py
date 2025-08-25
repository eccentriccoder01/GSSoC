import re
import requests
from collections import defaultdict
from datetime import datetime, timezone, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========= CONFIG =========
GITHUB_TOKEN = "<Your_GitHub_PAT>"
REPO = "eccentriccoder01/TalkHeal" #Replace with your Repo
LABEL_REQUIRED = "gssoc25"
POINTS_MAP = {"level 1": 3, "level 2": 7, "level 3": 10}

SHEET1_URL = "https://docs.google.com/spreadsheets/d/1icNvrmtp0eeJn5RIt2f8u8fcD_eRsRFpvhLIxBk3WEs/edit" #Contributor Details
SHEET2_URL = "<Your_Sheet_Link>"
CREDS_FILE = "credentials.json"  # Google Service Account creds, download this from the Console and place it in the same directory

IST = timezone(timedelta(hours=5, minutes=30))
START_DATETIME = datetime(2025, 8, 9, 16, 50, 0, tzinfo=IST)
END_DATETIME   = datetime(2025, 8, 25, 12, 10, 00, tzinfo=IST) 

def normalize_github(value):
    """Extract GitHub username from any form of input."""
    if not isinstance(value, str) or not value.strip():
        return ""
    value = value.strip().lower()
    value = re.sub(r'^https?://', '', value)
    value = re.sub(r'^www\.', '', value)
    if value.startswith("github.com/"):
        value = value.split("/", 1)[1]
    value = value.split("?")[0].split("#")[0].strip("/")
    return value


def fetch_all_prs():
    """Fetch all closed PRs from the repo."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    prs = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{REPO}/pulls"
        params = {"state": "closed", "per_page": 100, "page": page}
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        prs.extend(batch)
        page += 1
    return prs


def filter_and_score_prs(prs):
    """Filter merged PRs with gssoc25 label and score them, within time slot."""
    data = []
    for pr in prs:
        merged_at = pr.get("merged_at")
        if not merged_at:
            continue
        merged_time = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
        if not (START_DATETIME <= merged_time <= END_DATETIME):
            continue

        labels = [l["name"].lower() for l in pr["labels"]]
        if LABEL_REQUIRED in labels:
            points = 0
            for label in labels:
                if label in POINTS_MAP:
                    points = POINTS_MAP[label]
                    break
            data.append({
                "github_user": normalize_github(pr["user"]["html_url"]),
                "points": points
            })
    return data


def aggregate_points(data):
    """Sum points per GitHub username."""
    agg = defaultdict(int)
    for entry in data:
        agg[entry["github_user"]] += entry["points"]
    return agg


def load_sheet_data(url):
    """Load Google Sheet data."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    return client.open_by_url(url)


def main():
    print("📡 Fetching PRs...")
    prs = fetch_all_prs()
    
    print(f"🔍 Found {len(prs)} closed PRs. Filtering & scoring...")
    data = filter_and_score_prs(prs)
    
    print(f"✅ {len(data)} PRs match criteria in given time slot. Aggregating points...")
    points_per_user = aggregate_points(data)
    
    print("📄 Loading Sheet 1 for contributor details...")
    sheet1 = load_sheet_data(SHEET1_URL)
    sheet1_data = sheet1.get_worksheet(0).get_all_records()
    
    github_to_details = {}
    for row in sheet1_data:
        github_val = row.get("github_url", "")
        username = normalize_github(github_val)
        if username:
            full_name = str(row.get("full_name", "")).strip()
            email = str(row.get("email", "")).strip()
            github_to_details[username] = (full_name, email)
    
    print("📝 Updating Sheet 2...")
    sheet2 = load_sheet_data(SHEET2_URL)
    ws2 = sheet2.get_worksheet(0)
    
    rows_to_add = []
    for github_user, total_points in points_per_user.items():
        name, email = github_to_details.get(github_user, ("", ""))
        github_link = f"https://github.com/{github_user}"
        rows_to_add.append([name, email, github_link, total_points])
    
    for i, row in enumerate(rows_to_add, start=2):
        ws2.update(f"A{i}:D{i}", [row])
    
    print("✅ Sheet 2 updated successfully!")


if __name__ == "__main__":
    main()
