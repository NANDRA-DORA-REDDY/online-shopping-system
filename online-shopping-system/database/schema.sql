-- Online Shopping System
-- MySQL database schema based on the college DBMS project documentation.

CREATE DATABASE IF NOT EXISTS OnlineShopping;
USE OnlineShopping;

CREATE TABLE IF NOT EXISTS Customer (
    Customer_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_Name VARCHAR(50) NOT NULL,
    Email VARCHAR(80) UNIQUE,
    Phone VARCHAR(15),
    Address VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Category (
    Category_ID INT PRIMARY KEY AUTO_INCREMENT,
    Category_Name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Product (
    Product_ID INT PRIMARY KEY AUTO_INCREMENT,
    Product_Name VARCHAR(80) NOT NULL,
    Category_ID INT NOT NULL,
    Price DECIMAL(10,2) NOT NULL CHECK (Price > 0),
    Stock INT NOT NULL DEFAULT 0 CHECK (Stock >= 0),
    FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID)
);

CREATE TABLE IF NOT EXISTS Cart (
    Cart_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID),
    FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID)
);

CREATE TABLE IF NOT EXISTS Orders (
    Order_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_ID INT NOT NULL,
    Order_Date DATE NOT NULL,
    Total_Amount DECIMAL(10,2) CHECK (Total_Amount >= 0),
    Order_Status VARCHAR(20) DEFAULT 'Placed',
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);

CREATE TABLE IF NOT EXISTS Order_Items (
    Order_Item_ID INT PRIMARY KEY AUTO_INCREMENT,
    Order_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    Price DECIMAL(10,2) NOT NULL CHECK (Price > 0),
    FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID),
    FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID)
);

CREATE TABLE IF NOT EXISTS Payment (
    Payment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Order_ID INT NOT NULL UNIQUE,
    Payment_Date DATE,
    Payment_Method VARCHAR(20),
    Payment_Status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID)
);

CREATE TABLE IF NOT EXISTS Delivery (
    Delivery_ID INT PRIMARY KEY AUTO_INCREMENT,
    Order_ID INT NOT NULL UNIQUE,
    Delivery_Address VARCHAR(100) NOT NULL,
    Delivery_Date DATE,
    Delivery_Status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID)
);

-- The report also adds Pincode to Customer.
ALTER TABLE Customer ADD COLUMN IF NOT EXISTS Pincode VARCHAR(10);

-- Sample data from the project documentation.
INSERT IGNORE INTO Customer
    (Customer_ID, Customer_Name, Email, Phone, Address)
VALUES
    (1, 'Ravi Teja', 'ravi@example.com', '9876543210', 'Kakinada');

INSERT IGNORE INTO Category (Category_ID, Category_Name)
VALUES (1, 'Electronics');

INSERT IGNORE INTO Product
    (Product_ID, Product_Name, Category_ID, Price, Stock)
VALUES
    (101, 'Headphones', 1, 1499.00, 50);

-- A second sample category/product makes the website more useful for demonstration.
INSERT IGNORE INTO Category (Category_ID, Category_Name)
VALUES
    (2, 'Accessories'),
    (3, 'Home & Kitchen');

INSERT IGNORE INTO Product
    (Product_ID, Product_Name, Category_ID, Price, Stock)
VALUES
    (102, 'Wireless Mouse', 2, 799.00, 35),
    (103, 'USB-C Cable', 2, 399.00, 80),
    (104, 'Desk Lamp', 3, 1199.00, 20),
    (105, 'Bluetooth Speaker', 1, 1999.00, 25);

-- Representative records documented in the project report.
INSERT IGNORE INTO Cart (Cart_ID, Customer_ID, Product_ID, Quantity)
VALUES (5, 1, 101, 1);

INSERT IGNORE INTO Orders
    (Order_ID, Customer_ID, Order_Date, Total_Amount, Order_Status)
VALUES
    (1001, 1, '2026-08-10', 1499.00, 'Placed');

INSERT IGNORE INTO Order_Items
    (Order_Item_ID, Order_ID, Product_ID, Quantity, Price)
VALUES
    (1, 1001, 101, 1, 1499.00);

INSERT IGNORE INTO Payment
    (Payment_ID, Order_ID, Payment_Date, Payment_Method, Payment_Status)
VALUES
    (1, 1001, '2026-08-10', 'UPI', 'Paid');

INSERT IGNORE INTO Delivery
    (Delivery_ID, Order_ID, Delivery_Address, Delivery_Date, Delivery_Status)
VALUES
    (1, 1001, 'Kakinada', '2026-08-14', 'Shipped');

-- View documented in the project report.
CREATE OR REPLACE VIEW Order_Summary AS
SELECT
    o.Order_ID,
    c.Customer_Name,
    o.Order_Date,
    o.Total_Amount,
    o.Order_Status
FROM Orders o
JOIN Customer c ON o.Customer_ID = c.Customer_ID;

-- Example queries from the project:
-- SELECT * FROM Product;
-- SELECT Product_Name, Price FROM Product WHERE Price < 2000;
-- SELECT Category_ID, COUNT(*) AS Total FROM Product GROUP BY Category_ID;
-- SELECT * FROM Orders ORDER BY Order_Date DESC;
-- SELECT * FROM Order_Summary WHERE Total_Amount > 5000;
