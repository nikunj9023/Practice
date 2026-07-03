# Round 4

# Design Database For Business ERP Modules Customer Vendor Invoice Purchase Sales Payment Inventory Warehouse Employee Attendance Payroll

#create database erp_system;
Create table customer(
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(100) UNIQUE,
    customer_phone VARCHAR(15),
    customer_address VARCHAR(255)
);

#create table vendor(
    vendor_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_name VARCHAR(100) NOT NULL,
    vendor_email VARCHAR(100) UNIQUE,
    vendor_phone VARCHAR(15),
    vendor_address VARCHAR(255)
);

#create table invoice(
    invoice_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    vendor_id INT,
    invoice_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id)
);

#create table purchase(
    purchase_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_id INT,
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id)
);

#create table sales(
    sales_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    sales_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

#create table payment(
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT,
    payment_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id)
);

#create table inventory(
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);


#create table warehouse(
    warehouse_id INT PRIMARY KEY AUTO_INCREMENT,
    warehouse_name VARCHAR(100) NOT NULL,
    warehouse_location VARCHAR(255) NOT NULL
);

#create table employee(
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_name VARCHAR(100) NOT NULL,
    employee_email VARCHAR(100) UNIQUE,
    employee_phone VARCHAR(15),
    employee_address VARCHAR(255),
    hire_date DATE NOT NULL,
    salary DECIMAL(10, 2) NOT NULL
);

#create table attendance(
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Leave') NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

#create table payroll(
    payroll_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    payroll_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);



#Relationships between modules:
#Customer - Invoice (One-to-Many)
#Vendor - Invoice (One-to-Many)
#Vendor - Purchase (One-to-Many)
#Customer - Sales (One-to-Many)
#Invoice - Payment (One-to-Many)
#Inventory - Warehouse (Many-to-One)
#Employee - Attendance (One-to-Many)
#Employee - Payroll (One-to-Many)
