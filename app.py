import os
from datetime import date
from decimal import Decimal

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=None)
CORS(app)


def db_config():
    # Works with Railway MySQL environment variables and local MySQL setups[cite: 4, 5].
    return {
        "host": os.getenv("MYSQLHOST", os.getenv("DB_HOST", "localhost")),
        "port": int(os.getenv("MYSQLPORT", os.getenv("DB_PORT", "3306"))),
        "user": os.getenv("MYSQLUSER", os.getenv("DB_USER", "root")),
        "password": os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD", "")),
        "database": os.getenv("MYSQLDATABASE", os.getenv("DB_NAME", "OnlineShopping")),
    }


def get_connection():
    return mysql.connector.connect(**db_config())


def json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def rows_to_dicts(cursor):
    rows = cursor.fetchall()
    if not rows:
        return []
    # Handles dictionary cursors safely without overwriting dict values with key names[cite: 5]
    if isinstance(rows[0], dict):
        return [{k: json_safe(v) for k, v in row.items()} for row in rows]
    # Fallback for standard tuple cursors[cite: 5]
    columns = cursor.column_names
    return [
        {column: json_safe(value) for column, value in zip(columns, row)}
        for row in rows
    ]


@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:path>")
def frontend_files(path):
    full_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/health")
def health():
    conn = None
    try:
        conn = get_connection()
        return jsonify({"status": "ok", "database": "connected"})
    except Error as e:
        return jsonify({"status": "error", "database": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()

    if not name or not email:
        return jsonify({"error": "Name and email are required."}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT Customer_ID FROM Customer WHERE Email = %s", (email,))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": "An account with this email already exists."}), 409

        cursor.execute(
            """
            INSERT INTO Customer (Customer_Name, Email, Phone, Address)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, phone or None, address or None),
        )
        customer_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "message": "Registration successful.",
            "customer": {
                "Customer_ID": customer_id,
                "Customer_Name": name,
                "Email": email,
            },
        }), 201

    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"error": "Email is required."}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT Customer_ID, Customer_Name, Email, Phone, Address, Pincode
            FROM Customer
            WHERE Email = %s
            """,
            (email,),
        )
        customer = cursor.fetchone()

        if not customer:
            return jsonify({"error": "Account not found. Please register first."}), 404

        return jsonify({"customer": customer})

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.get("/api/products")
def products():
    category_id = request.args.get("category_id")
    search = request.args.get("search", "").strip()

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT p.Product_ID, p.Product_Name, p.Category_ID,
                   c.Category_Name, p.Price, p.Stock
            FROM Product p
            JOIN Category c ON p.Category_ID = c.Category_ID
            WHERE 1=1
        """
        params = []

        if category_id:
            query += " AND p.Category_ID = %s"
            params.append(category_id)

        if search:
            query += " AND (p.Product_Name LIKE %s OR c.Category_Name LIKE %s)"
            like = f"%{search}%"
            params.extend([like, like])

        query += " ORDER BY p.Product_ID"

        cursor.execute(query, tuple(params))
        result = rows_to_dicts(cursor)

        return jsonify(result)

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.get("/api/categories")
def categories():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Category_ID, Category_Name FROM Category ORDER BY Category_Name")
        result = rows_to_dicts(cursor)
        return jsonify(result)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.get("/api/cart/<int:customer_id>")
def get_cart(customer_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT ca.Cart_ID, ca.Product_ID, p.Product_Name, p.Price,
                   p.Stock, ca.Quantity, (p.Price * ca.Quantity) AS Subtotal
            FROM Cart ca
            JOIN Product p ON ca.Product_ID = p.Product_ID
            WHERE ca.Customer_ID = %s
            ORDER BY ca.Cart_ID DESC
            """,
            (customer_id,),
        )
        result = rows_to_dicts(cursor)
        return jsonify(result)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.post("/api/cart")
def add_to_cart():
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not customer_id or not product_id or quantity < 1:
        return jsonify({"error": "Customer, product and valid quantity are required."}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT Stock FROM Product WHERE Product_ID = %s",
            (product_id,),
        )
        product = cursor.fetchone()
        if not product:
            return jsonify({"error": "Product not found."}), 404
        if product["Stock"] < quantity:
            return jsonify({"error": "Not enough stock available."}), 400

        cursor.execute(
            """
            SELECT Cart_ID, Quantity
            FROM Cart
            WHERE Customer_ID = %s AND Product_ID = %s
            """,
            (customer_id, product_id),
        )
        existing = cursor.fetchone()

        if existing:
            new_quantity = existing["Quantity"] + quantity
            if new_quantity > product["Stock"]:
                return jsonify({"error": "Requested quantity exceeds available stock."}), 400
            cursor.execute(
                "UPDATE Cart SET Quantity = %s WHERE Cart_ID = %s",
                (new_quantity, existing["Cart_ID"]),
            )
        else:
            cursor.execute(
                """
                INSERT INTO Cart (Customer_ID, Product_ID, Quantity)
                VALUES (%s, %s, %s)
                """,
                (customer_id, product_id, quantity),
            )

        conn.commit()
        return jsonify({"message": "Product added to cart."}), 201

    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.put("/api/cart/<int:cart_id>")
def update_cart(cart_id):
    data = request.get_json(silent=True) or {}
    quantity = int(data.get("quantity", 0))

    if quantity < 1:
        return jsonify({"error": "Quantity must be at least 1."}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT ca.Cart_ID, p.Stock
            FROM Cart ca JOIN Product p ON ca.Product_ID = p.Product_ID
            WHERE ca.Cart_ID = %s
            """,
            (cart_id,),
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Cart item not found."}), 404
        if quantity > row["Stock"]:
            return jsonify({"error": "Quantity exceeds available stock."}), 400

        cursor.execute(
            "UPDATE Cart SET Quantity = %s WHERE Cart_ID = %s",
            (quantity, cart_id),
        )
        conn.commit()
        return jsonify({"message": "Cart updated."})

    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.delete("/api/cart/<int:cart_id>")
def delete_cart(cart_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Cart WHERE Cart_ID = %s", (cart_id,))
        conn.commit()
        return jsonify({"message": "Item removed from cart."})
    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.post("/api/orders")
def place_order():
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customer_id")
    address = data.get("address", "").strip()
    payment_method = data.get("payment_method", "COD").strip()

    if not customer_id or not address:
        return jsonify({"error": "Customer and delivery address are required."}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT ca.Cart_ID, ca.Product_ID, ca.Quantity,
                   p.Product_Name, p.Price, p.Stock
            FROM Cart ca
            JOIN Product p ON ca.Product_ID = p.Product_ID
            WHERE ca.Customer_ID = %s
            FOR UPDATE
            """,
            (customer_id,),
        )
        cart_items = cursor.fetchall()

        if not cart_items:
            conn.rollback()
            return jsonify({"error": "Your cart is empty."}), 400

        total = Decimal("0.00")
        for item in cart_items:
            if item["Quantity"] > item["Stock"]:
                conn.rollback()
                return jsonify({
                    "error": f"Insufficient stock for {item['Product_Name']}."
                }), 400
            total += item["Price"] * item["Quantity"]

        cursor.execute(
            """
            INSERT INTO Orders (Customer_ID, Order_Date, Total_Amount, Order_Status)
            VALUES (%s, %s, %s, 'Placed')
            """,
            (customer_id, date.today(), total),
        )
        order_id = cursor.lastrowid

        for item in cart_items:
            cursor.execute(
                """
                INSERT INTO Order_Items
                    (Order_ID, Product_ID, Quantity, Price)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, item["Product_ID"], item["Quantity"], item["Price"]),
            )

            cursor.execute(
                """
                UPDATE Product
                SET Stock = Stock - %s
                WHERE Product_ID = %s AND Stock >= %s
                """,
                (item["Quantity"], item["Product_ID"], item["Quantity"]),
            )
            if cursor.rowcount != 1:
                raise ValueError("Stock changed while processing the order.")

        cursor.execute(
            """
            INSERT INTO Payment
                (Order_ID, Payment_Date, Payment_Method, Payment_Status)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, date.today(), payment_method, "Paid" if payment_method == "COD" else "Pending"),
        )

        cursor.execute(
            """
            INSERT INTO Delivery
                (Order_ID, Delivery_Address, Delivery_Status)
            VALUES (%s, %s, 'Pending')
            """,
            (order_id, address),
        )

        cursor.execute("DELETE FROM Cart WHERE Customer_ID = %s", (customer_id,))
        conn.commit()

        return jsonify({
            "message": "Order placed successfully.",
            "order_id": order_id,
            "total_amount": float(total),
        }), 201

    except (Error, ValueError) as e:
        if conn and conn.is_connected():
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.get("/api/orders/<int:customer_id>")
def get_orders(customer_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT o.Order_ID, o.Order_Date, o.Total_Amount, o.Order_Status,
                   p.Payment_Method, p.Payment_Status,
                   d.Delivery_Address, d.Delivery_Date, d.Delivery_Status
            FROM Orders o
            LEFT JOIN Payment p ON o.Order_ID = p.Order_ID
            LEFT JOIN Delivery d ON o.Order_ID = d.Order_ID
            WHERE o.Customer_ID = %s
            ORDER BY o.Order_Date DESC, o.Order_ID DESC
            """,
            (customer_id,),
        )
        orders = rows_to_dicts(cursor)

        for order in orders:
            cursor.execute(
                """
                SELECT oi.Product_ID, pr.Product_Name, oi.Quantity, oi.Price
                FROM Order_Items oi
                JOIN Product pr ON oi.Product_ID = pr.Product_ID
                WHERE oi.Order_ID = %s
                """,
                (order["Order_ID"],),
            )
            order["items"] = rows_to_dicts(cursor)

        return jsonify(orders)

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)