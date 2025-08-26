# 📘 README – Contributor Points Automation (TalkHeal)

This repo provides **two automation scripts** for fetching and scoring contributors’ merged PRs on a GitHub repo, then updating a Google Sheet with their details and total points.

---

## 📂 Scripts

1. **`update_contributors_alltime_talkheal.py`**

   * Fetches all merged PRs (with specific labels) since the beginning of the repository.
   * Updates contributor points in the Google Sheet.

2. **`update_contributors_timeslot_talkheal.py`**

   * Same as above, but **only for PRs merged within a given date-time window** (useful for phases or weekly scoring).
   * Dates can be set in **IST** or any timezone via `datetime` config.

---

## ✅ Prerequisites

### 1. Python

* Python **3.8+** installed.
* Install required packages:

  ```bash
  pip install requests gspread oauth2client
  ```

### 2. GitHub Personal Access Token (PAT)

* Go to [GitHub → Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens).
* Generate a classic token with scopes:

  * `repo` (for private repos)
  * `read:org` (optional if organization repos)
* Copy the token and paste it into the script:

  ```python
  GITHUB_TOKEN = "<Your_GitHub_PAT>"
  ```

⚠️ Keep this token **secret**. Do not commit it to GitHub.

---

### 3. Google Sheets Setup

Both scripts read contributor details (Sheet 1) and write points to another sheet (Sheet 2).

* **Sheet 1 (Contributor Details)** should have columns (Link is already put, you don't have to change this):

  * `full_name`
  * `email`
  * `github_url`
  * `linkedin_url` (optional)
* **Sheet 2 (Scored Contributors)** will be updated with:

  * Full Name | Email | GitHub Profile | Points

#### Service Account & Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a **new project** (or use existing).
3. Enable the **Google Sheets API**.
4. Create **Service Account credentials** → download JSON → save as `credentials.json` in the same folder as the scripts.
5. Share both Google Sheets (`SHEET1_URL`, `SHEET2_URL`) with the **service account email** (from the JSON) with **Editor permission**.

---

## ⚙️ Configuration

### Common Fields

* **Repository**:

  ```python
  REPO = "eccentriccoder01/TalkHeal"  # format: "owner/repo"
  ```
* **Label required**:

  ```python
  LABEL_REQUIRED = "gssoc25"
  ```
* **Points mapping**:

  ```python
  POINTS_MAP = {"level 1": 3, "level 2": 7, "level 3": 10}
  ```
* **Google Sheets URLs**:

  ```python
  SHEET1_URL = "https://docs.google.com/spreadsheets/..."  # Contributor Details
  SHEET2_URL = "https://docs.google.com/spreadsheets/..."  # Points Output
  ```

### Timeslot Script Only

* **Time Window (IST example)**:

  ```python
  from datetime import datetime, timezone, timedelta
  IST = timezone(timedelta(hours=5, minutes=30))

  START_DATETIME = datetime(2025, 8, 9, 16, 50, 0, tzinfo=IST)
  END_DATETIME   = datetime(2025, 8, 25, 12, 10, 0, tzinfo=IST)
  ```
* You can change timezone as needed (`timezone.utc` for UTC, etc.).

---

## ▶️ Running the Scripts

### All-time Contributor Points

```bash
python update_contributors_alltime_talkheal.py
```

### Timeslot Contributor Points

```bash
python update_contributors_timeslot_talkheal.py
```

---

## 🛠️ Troubleshooting

* **403: The caller does not have permission**

  * Ensure you shared both sheets with your service account email.
  * Check that `credentials.json` is in the same directory.

* **DeprecationWarning about worksheet.update**

  * You can safely ignore this, or update to:

    ```python
    ws2.update(values=[row], range_name=f"A{i}:D{i}")
    ```

* **No PRs Found**

  * Ensure the repo and labels are correct.
  * PAT must have proper scopes.

* **Wrong timezone in timeslot script**

  * Double-check if you’re using `IST = timezone(timedelta(hours=5, 30))` for India.

---

## 📊 Example Output

After running, Sheet 2 will be updated like:

| Full Name   | Email                                     | GitHub                                               | Points |
| ----------- | ----------------------------------------- | ---------------------------------------------------- | ------ |
| Alice Smith | [alice@email.com](mailto:alice@email.com) | [https://github.com/alice](https://github.com/alice) | 10     |
| Bob Kumar   | [bob@email.com](mailto:bob@email.com)     | [https://github.com/bob](https://github.com/bob)     | 7      |