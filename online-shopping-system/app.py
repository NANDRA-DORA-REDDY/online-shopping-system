import os
import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date

st.set_page_config(page_title="Online Shopping System", page_icon="🛒", layout="wide")

def config():
    return {
        "host": os.getenv("MYSQLHOST", os.getenv("DB_HOST", "localhost")),
        "port": int(os.getenv("MYSQLPORT", os.getenv("DB_PORT", "3306"))),
        "user": os.getenv("MYSQLUSER", os.getenv("DB_USER", "root")),
        "password": os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD", "")),
        "database": os.getenv("MYSQLDATABASE", os.getenv("DB_NAME", "online_shopping")),
    }

def query(sql, params=(), fetch=True):
    conn = cur = None
    try:
        conn = mysql.connector.connect(**config())
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        if fetch: return cur.fetchall()
        conn.commit()
        return True
    except Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()

if "cart" not in st.session_state: st.session_state.cart = []
if "customer_id" not in st.session_state: st.session_state.customer_id = None
if "customer_name" not in st.session_state: st.session_state.customer_name = None

st.title("🛒 Online Shopping System")
st.caption("DBMS Cornerstone Project — Streamlit + Python + MySQL")

with st.sidebar:
    page = st.radio("Navigation", ["Home","Products","Cart","Checkout","Orders","Login/Register"])
    st.metric("Cart Items", sum(x["quantity"] for x in st.session_state.cart))
    if st.session_state.customer_name:
        st.success(f"Logged in: {st.session_state.customer_name}")
        if st.button("Logout"):
            st.session_state.customer_id = None
            st.session_state.customer_name = None
            st.rerun()

if page == "Home":
    st.subheader("Welcome")
    st.write("Online shopping system with customers, categories, products, cart, orders, payments and delivery.")
    a,b,c = st.columns(3)
    a.info("📦 Products\n\nBrowse products and categories.")
    b.info("🛒 Cart\n\nAdd and manage products.")
    c.info("🚚 Orders\n\nPlace and view orders.")

elif page == "Login/Register":
    st.subheader("Customer Login / Registration")
    t1,t2 = st.tabs(["Login","Register"])
    with t1:
        email = st.text_input("Email")
        if st.button("Login", type="primary"):
            rows = query("SELECT Customer_ID,Customer_Name FROM CUSTOMER WHERE Email=%s",(email,))
            if rows:
                st.session_state.customer_id = rows[0]["Customer_ID"]
                st.session_state.customer_name = rows[0]["Customer_Name"]
                st.success("Login successful.")
                st.rerun()
            else: st.error("Customer not found. Register first.")
    with t2:
        name=st.text_input("Full Name")
        email=st.text_input("Email", key="reg_email")
        phone=st.text_input("Phone")
        address=st.text_area("Address")
        if st.button("Register", type="primary"):
            if not name or not email: st.warning("Name and email are required.")
            elif query("SELECT Customer_ID FROM CUSTOMER WHERE Email=%s",(email,)): st.error("Email already registered.")
            elif query("INSERT INTO CUSTOMER(Customer_Name,Email,Phone,Address) VALUES(%s,%s,%s,%s)",(name,email,phone,address),False):
                st.success("Registered. You can now login.")

elif page == "Products":
    st.subheader("🛍️ Products")
    cats=query("SELECT Category_ID,Category_Name FROM CATEGORY ORDER BY Category_Name") or []
    opts={"All Categories":None}|{x["Category_Name"]:x["Category_ID"] for x in cats}
    selected=st.selectbox("Category",list(opts))
    search=st.text_input("Search product")
    sql="""SELECT p.Product_ID,p.Product_Name,c.Category_Name,p.Price,p.Stock
           FROM PRODUCT p JOIN CATEGORY c ON p.Category_ID=c.Category_ID WHERE 1=1"""
    params=[]
    if opts[selected] is not None: sql+=" AND p.Category_ID=%s"; params.append(opts[selected])
    if search: sql+=" AND p.Product_Name LIKE %s"; params.append("%"+search+"%")
    products=query(sql+" ORDER BY p.Product_ID",tuple(params)) or []
    for p in products:
        with st.container(border=True):
            c1,c2,c3,c4=st.columns([3,2,1,1])
            c1.write(f"**{p['Product_Name']}**"); c1.caption(p["Category_Name"])
            c2.write(f"₹{float(p['Price']):,.2f}"); c3.write(f"Stock: {p['Stock']}")
            if p["Stock"]>0:
                q=c4.number_input("Qty",1,int(p["Stock"]),1,key=f"q{p['Product_ID']}")
                if st.button("Add",key=f"a{p['Product_ID']}"):
                    found=next((x for x in st.session_state.cart if x["product_id"]==p["Product_ID"]),None)
                    if found: found["quantity"]+=q
                    else: st.session_state.cart.append({"product_id":p["Product_ID"],"name":p["Product_Name"],"price":float(p["Price"]),"quantity":q})
                    st.success("Added to cart.")
            else: c4.button("Out of stock",disabled=True,key=f"o{p['Product_ID']}")

elif page == "Cart":
    st.subheader("🛒 Shopping Cart")
    if not st.session_state.cart: st.info("Cart is empty.")
    else:
        total=0
        for i,item in enumerate(st.session_state.cart):
            sub=item["price"]*item["quantity"]; total+=sub
            a,b,c=st.columns([4,2,1])
            a.write(f"**{item['name']}**")
            item["quantity"]=b.number_input("Quantity",1,value=item["quantity"],key=f"cq{i}")
            if c.button("Remove",key=f"r{i}"):
                st.session_state.cart.pop(i); st.rerun()
            st.write(f"Subtotal: ₹{sub:,.2f}")
        st.divider(); st.subheader(f"Total: ₹{total:,.2f}")

elif page == "Checkout":
    st.subheader("💳 Checkout")
    if not st.session_state.customer_id: st.warning("Please login first.")
    elif not st.session_state.cart: st.info("Cart is empty.")
    else:
        customer=query("SELECT * FROM CUSTOMER WHERE Customer_ID=%s",(st.session_state.customer_id,))
        customer=customer[0] if customer else {}
        total=sum(x["price"]*x["quantity"] for x in st.session_state.cart)
        st.write(f"**Order Total: ₹{total:,.2f}**")
        address=st.text_area("Delivery Address",value=customer.get("Address","") or "")
        method=st.selectbox("Payment Method",["Cash on Delivery","UPI","Card"])
        if st.button("Place Order",type="primary"):
            conn=cur=None
            try:
                conn=mysql.connector.connect(**config()); cur=conn.cursor()
                cur.execute("INSERT INTO ORDERS(Customer_ID,Order_Date,Total_Amount,Order_Status) VALUES(%s,%s,%s,%s)",(st.session_state.customer_id,date.today(),total,"Placed"))
                oid=cur.lastrowid
                for x in st.session_state.cart:
                    cur.execute("INSERT INTO ORDER_ITEMS(Order_ID,Product_ID,Quantity,Price) VALUES(%s,%s,%s,%s)",(oid,x["product_id"],x["quantity"],x["price"]))
                    cur.execute("UPDATE PRODUCT SET Stock=Stock-%s WHERE Product_ID=%s AND Stock>=%s",(x["quantity"],x["product_id"],x["quantity"]))
                cur.execute("INSERT INTO PAYMENT(Order_ID,Payment_Date,Payment_Method,Payment_Status) VALUES(%s,%s,%s,%s)",(oid,date.today(),method,"Pending"))
                cur.execute("INSERT INTO DELIVERY(Order_ID,Delivery_Address,Delivery_Status) VALUES(%s,%s,%s)",(oid,address,"Processing"))
                conn.commit(); st.session_state.cart=[]; st.success(f"Order #{oid} placed successfully!"); st.balloons()
            except Error as e:
                if conn: conn.rollback()
                st.error(f"Could not place order: {e}")
            finally:
                if cur: cur.close()
                if conn: conn.close()

elif page == "Orders":
    st.subheader("📋 My Orders")
    if not st.session_state.customer_id: st.warning("Please login first.")
    else:
        orders=query("SELECT * FROM ORDERS WHERE Customer_ID=%s ORDER BY Order_ID DESC",(st.session_state.customer_id,)) or []
        if not orders: st.info("No orders found.")
        for o in orders:
            with st.expander(f"Order #{o['Order_ID']} — ₹{float(o['Total_Amount']):,.2f} — {o['Order_Status']}"):
                st.write(f"Date: {o['Order_Date']}")
                items=query("""SELECT p.Product_Name,oi.Quantity,oi.Price FROM ORDER_ITEMS oi JOIN PRODUCT p ON oi.Product_ID=p.Product_ID WHERE oi.Order_ID=%s""",(o["Order_ID"],)) or []
                for x in items: st.write(f"- {x['Product_Name']} × {x['Quantity']} @ ₹{float(x['Price']):,.2f}")
                d=query("SELECT Delivery_Status,Delivery_Address FROM DELIVERY WHERE Order_ID=%s",(o["Order_ID"],))
                if d: st.write(f"Delivery: {d[0]['Delivery_Status']}"); st.write(f"Address: {d[0]['Delivery_Address']}")
