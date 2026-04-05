import pandas as pd
from pathlib import Path

# This finds the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# These point to my data folder and output folder
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# Read the CSV files into pandas tables
google_df = pd.read_csv(DATA_DIR / "google_users.csv")
okta_df = pd.read_csv(DATA_DIR / "okta_users.csv")
apple_df = pd.read_csv(DATA_DIR / "apple_devices.csv")

# Clean up email columns so they match better
# .strip() removes extra spaces
# .lower() makes everything lowercase
google_df["email"] = google_df["email"].str.strip().str.lower()
okta_df["email"] = okta_df["email"].str.strip().str.lower()
apple_df["assigned_email"] = apple_df["assigned_email"].str.strip().str.lower()

# This list will store all the problems I find
issues = []

# -------------------------------
# Check 1: In Google but not Okta
# -------------------------------

# Turn Okta emails into a set so lookup is faster
okta_emails = set(okta_df["email"])

# Go through each Google user and see if they exist in Okta
for _, row in google_df.iterrows():
    if row["email"] not in okta_emails:
        issues.append({
            "email": row["email"],
            "issue": "Exists in Google but missing in Okta"
        })

# ---------------------------------------------
# Check 2: Suspended in Google but active in Okta
# ---------------------------------------------

# Merge the two tables together by email
merged = google_df.merge(okta_df, on="email", how="inner", suffixes=("_google", "_okta"))

# Look for users whose status does not match
for _, row in merged.iterrows():
    if str(row["status_google"]).upper() == "SUSPENDED" and str(row["status_okta"]).upper() == "ACTIVE":
        issues.append({
            "email": row["email"],
            "issue": "Suspended in Google but still active in Okta"
        })

# -------------------------------
# Check 3: Okta users without MFA
# -------------------------------

# Go through Okta users and check if MFA is turned on
for _, row in okta_df.iterrows():
    if str(row["mfa_enabled"]).upper() != "TRUE":
        issues.append({
            "email": row["email"],
            "issue": "Okta account without MFA enabled"
        })

# -----------------------------------------
# Check 4: Okta users with no Apple device
# -----------------------------------------

# Make a set of emails that do have an Apple device assigned
device_emails = set(
    apple_df["assigned_email"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.lower()
)

# Go through Okta users and see who is missing from that list
for _, row in okta_df.iterrows():
    if row["email"] not in device_emails:
        issues.append({
            "email": row["email"],
            "issue": "Okta user has no assigned Apple device"
        })

# Turn the list of issues into a table
report_df = pd.DataFrame(issues)

# Make sure the output folder exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Save the report as a CSV file
report_path = OUTPUT_DIR / "drift_report.csv"
report_df.to_csv(report_path, index=False)

# Print where the report was saved
print(f"Report written to: {report_path}")

# Print the report in the terminal too
print(report_df if not report_df.empty else "No issues found.")