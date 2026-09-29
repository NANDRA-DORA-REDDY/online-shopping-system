# Online Shopping System

DBMS Cornerstone Project — Online Shopping System.

## Technology

- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Database: MySQL
- Connectivity: MySQL Connector/Python
- Development: VS Code
- Deployment target: Railway
- Source control: GitHub

## Project structure

```text
online-shopping-system/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── products.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   ├── css/style.css
│   └── js/
├── database/schema.sql
├── Procfile
├── .gitignore
└── README.md
```

## Local setup

1. Install Python 3.11+.
2. Install MySQL 8.x.
3. Open MySQL Workbench.
4. Run `database/schema.sql`.
5. Open a terminal in the project folder.
6. Create a virtual environment:

```bash
python -m venv .venv
```

7. Activate it on Windows:

```bash
.venv\Scripts\activate
```

8. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

9. Set database variables if your MySQL password is not empty:

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_PASSWORD
DB_NAME=OnlineShopping
```

You can also create a `.env` file for local use, but `.env` is ignored by Git.

10. Start the server:

```bash
python backend/app.py
```

11. Open:

```text
http://localhost:5000
```

## Railway deployment

The application reads the Railway MySQL variables:

- MYSQLHOST
- MYSQLPORT
- MYSQLUSER
- MYSQLPASSWORD
- MYSQLDATABASE

The `Procfile` starts the Flask application with Gunicorn.

After creating a Railway MySQL service, run `database/schema.sql` against that database once, then deploy the GitHub repository.

## Main database entities

The project documentation defines these eight core entities:

- Customer
- Category
- Product
- Cart
- Orders
- Order_Items
- Payment
- Delivery

## Notes

The login is intentionally simple because the documented Customer table does not contain a password column. It uses the customer's email for the demonstration. For a production system, authentication should be implemented separately with securely hashed passwords.
