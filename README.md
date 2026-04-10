# Identity Drift Audit

A lightweight proof of concept for identifying identity drift across core school systems (Google Workspace, Okta, and device inventory), with flexible checks that can be adapted to district security and access policies.

## What it checks
- users in Google but missing in Okta
- suspended Google users still active in Okta
- Okta users without MFA
- Okta users with no assigned Apple device

## Tech used
- Python
- pandas
- CSV exports

## How to run
```bash
pip install -r requirements.txt
python src/audit.py