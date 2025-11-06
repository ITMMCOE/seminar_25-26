# RetailIntel

**RetailIntel** — Smart Retail Analytics System for Small Shops

## Description
RetailIntel is a Flask-based web app that analyzes CSV sales data and generates interactive dashboards:
- Upload CSV (Date, Product, Units_Sold, Price, Stock)
- Monthly sales trend, Top products, Stock overview, Predictions
- Downloadable summary report

## Run locally (Windows)
1. Create & activate venv:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Run:

python app.py


Open http://127.0.0.1:5000 in browser.

Notes

Do not commit uploads/ or database.db.

Chart.js is loaded from CDN in templates.


---

## C. Initialize git (if not already) and commit

Open **PowerShell / VS Code terminal** inside your project folder and run:

```powershell
# go to project directory
cd "C:\Users\<your-user>\Projects\RetailIntel"

# initialize git repo (if not already)
git init

# set your identity (only first time)
git config user.name "Shahnawaz Shaikh"
git config user.email "your-email@example.com"

# add files, but .gitignore will exclude uploads/db
git add .

# commit
git commit -m "Initial commit: RetailIntel - full implementation"