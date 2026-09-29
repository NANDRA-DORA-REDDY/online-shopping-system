# Online Shopping System — Streamlit

This version uses Streamlit for the complete user interface and Python/MySQL for the backend/database.

## Run
1. Run `database/schema.sql` in MySQL Workbench.
2. Install packages:
   `pip install -r requirements.txt`
3. Set DB variables or use local defaults.
4. Run:
   `streamlit run app.py`

## Environment variables
MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE

## Railway
Use the same variables from the Railway MySQL service and start with:
`streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT`

Never commit database passwords to GitHub.
