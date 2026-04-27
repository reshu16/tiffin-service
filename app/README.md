# 🍱 TiffinBox — Online Tiffin Service Management System

A full-stack web application for managing an online tiffin delivery service,
built as a Final Year Major Project.

---

## 👨‍💻 Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.13, Flask                  |
| Database   | MySQL 8.0 with SQLAlchemy ORM       |
| Auth       | JWT (flask-jwt-extended)            |
| Frontend   | HTML5, CSS3, Bootstrap 5, JavaScript|
| Deployment | PythonAnywhere (free)               |

---

## 🚀 Features

### Customer
- Register / Login with JWT authentication
- Browse menu with category filters (Veg, Non-Veg, Special, Dessert)
- Add items to cart and place orders
- Choose Cash on Delivery or Online Payment
- View order history with real-time status tracking
- Subscribe to Daily / Weekly / Monthly tiffin plans
- Pause or cancel subscription anytime
- Submit reviews for delivered orders

### Admin
- Full dashboard with live statistics
- Manage all orders and update status
- Add / edit / delete menu items
- Manage users (activate / deactivate)
- View delivery agents and availability
- Revenue reports (last 7 days)

### Kitchen Manager
- View today's orders in real time (auto-refreshes every 30 seconds)
- Update order status: Confirm → Preparing → Ready for Delivery
- See item-wise counts per order

### Delivery Agent
- View assigned deliveries
- Update delivery status: Assigned → Picked Up → On The Way → Delivered
- Toggle availability on/off

---

## 🗄️ Database Schema (10 Tables)