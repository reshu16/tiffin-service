-- ============================================================
--  TIFFIN SERVICE MANAGEMENT SYSTEM
--  Database: tiffin_db
--  Engine: MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS tiffin_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tiffin_db;

-- ────────────────────────────────────────────────────────────
-- 1. USERS
--    Stores all user types: customer, admin, kitchen, delivery
-- ────────────────────────────────────────────────────────────
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    phone         VARCHAR(15)   NOT NULL UNIQUE,
    address       TEXT,
    role          ENUM('customer','admin','kitchen','delivery') NOT NULL DEFAULT 'customer',
    profile_image VARCHAR(255)  DEFAULT NULL,
    is_active     TINYINT(1)    NOT NULL DEFAULT 1,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ────────────────────────────────────────────────────────────
-- 2. MENU ITEMS
--    Tiffin dishes managed by kitchen/admin
-- ────────────────────────────────────────────────────────────
CREATE TABLE menu_items (
    item_id      INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(150)  NOT NULL,
    description  TEXT,
    price        DECIMAL(8,2)  NOT NULL,
    image_url    VARCHAR(255)  DEFAULT NULL,
    category     ENUM('veg','non-veg','special','dessert') NOT NULL DEFAULT 'veg',
    is_available TINYINT(1)    NOT NULL DEFAULT 1,
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ────────────────────────────────────────────────────────────
-- 3. SUBSCRIPTION PLANS
--    Daily / Weekly / Monthly tiffin plan options
-- ────────────────────────────────────────────────────────────
CREATE TABLE subscription_plans (
    plan_id     INT AUTO_INCREMENT PRIMARY KEY,
    plan_name   VARCHAR(100)  NOT NULL,
    duration    ENUM('daily','weekly','monthly') NOT NULL,
    price       DECIMAL(8,2)  NOT NULL,
    description TEXT,
    meals_per_day INT         NOT NULL DEFAULT 1,
    is_active   TINYINT(1)    NOT NULL DEFAULT 1,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ────────────────────────────────────────────────────────────
-- 4. USER SUBSCRIPTIONS
--    Records which customer has subscribed to which plan
-- ────────────────────────────────────────────────────────────
CREATE TABLE user_subscriptions (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    plan_id         INT          NOT NULL,
    start_date      DATE         NOT NULL,
    end_date        DATE         NOT NULL,
    status          ENUM('active','paused','cancelled','expired') NOT NULL DEFAULT 'active',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_us_user   FOREIGN KEY (user_id) REFERENCES users(user_id)              ON DELETE CASCADE,
    CONSTRAINT fk_us_plan   FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id) ON DELETE RESTRICT
);

-- ────────────────────────────────────────────────────────────
-- 5. ORDERS
--    Every tiffin order (single or subscription-based)
-- ────────────────────────────────────────────────────────────
CREATE TABLE orders (
    order_id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT           NOT NULL,
    subscription_id   INT           DEFAULT NULL,   -- NULL for one-time orders
    total_amount      DECIMAL(10,2) NOT NULL,
    status            ENUM('pending','confirmed','preparing','out_for_delivery',
                           'delivered','cancelled') NOT NULL DEFAULT 'pending',
    delivery_address  TEXT          NOT NULL,
    special_notes     TEXT          DEFAULT NULL,
    order_date        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ord_user  FOREIGN KEY (user_id)         REFERENCES users(user_id)             ON DELETE CASCADE,
    CONSTRAINT fk_ord_sub   FOREIGN KEY (subscription_id) REFERENCES user_subscriptions(subscription_id) ON DELETE SET NULL
);

-- ────────────────────────────────────────────────────────────
-- 6. ORDER ITEMS
--    Line items inside each order
-- ────────────────────────────────────────────────────────────
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id      INT          NOT NULL,
    item_id       INT          NOT NULL,
    quantity      INT          NOT NULL DEFAULT 1,
    unit_price    DECIMAL(8,2) NOT NULL,
    CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(order_id)     ON DELETE CASCADE,
    CONSTRAINT fk_oi_item  FOREIGN KEY (item_id)  REFERENCES menu_items(item_id)  ON DELETE RESTRICT
);

-- ────────────────────────────────────────────────────────────
-- 7. DELIVERY AGENTS
--    Extended profile for users with role = 'delivery'
-- ────────────────────────────────────────────────────────────
CREATE TABLE delivery_agents (
    agent_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT          NOT NULL UNIQUE,
    vehicle_number VARCHAR(20)  NOT NULL,
    is_available   TINYINT(1)   NOT NULL DEFAULT 1,
    rating         DECIMAL(3,2) NOT NULL DEFAULT 5.00,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_da_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ────────────────────────────────────────────────────────────
-- 8. DELIVERIES
--    Tracks which agent handles which order delivery
-- ────────────────────────────────────────────────────────────
CREATE TABLE deliveries (
    delivery_id    INT AUTO_INCREMENT PRIMARY KEY,
    order_id       INT          NOT NULL UNIQUE,
    agent_id       INT          NOT NULL,
    status         ENUM('assigned','picked_up','on_the_way','delivered','failed') NOT NULL DEFAULT 'assigned',
    assigned_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivered_at   DATETIME     DEFAULT NULL,
    delivery_notes TEXT         DEFAULT NULL,
    CONSTRAINT fk_del_order FOREIGN KEY (order_id)  REFERENCES orders(order_id)             ON DELETE CASCADE,
    CONSTRAINT fk_del_agent FOREIGN KEY (agent_id)  REFERENCES delivery_agents(agent_id)    ON DELETE RESTRICT
);

-- ────────────────────────────────────────────────────────────
-- 9. PAYMENTS
--    Payment record for each order
-- ────────────────────────────────────────────────────────────
CREATE TABLE payments (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    order_id       INT           NOT NULL UNIQUE,
    amount         DECIMAL(10,2) NOT NULL,
    method         ENUM('razorpay','upi','cod','wallet') NOT NULL DEFAULT 'razorpay',
    status         ENUM('pending','paid','failed','refunded') NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(200)  DEFAULT NULL,
    razorpay_order_id VARCHAR(200) DEFAULT NULL,
    paid_at        DATETIME      DEFAULT NULL,
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pay_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- ────────────────────────────────────────────────────────────
-- 10. REVIEWS
--     Customer ratings after delivery
-- ────────────────────────────────────────────────────────────
CREATE TABLE reviews (
    review_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT          NOT NULL,
    order_id   INT          NOT NULL,
    rating     TINYINT      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment    TEXT         DEFAULT NULL,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_review (user_id, order_id),
    CONSTRAINT fk_rev_user  FOREIGN KEY (user_id)  REFERENCES users(user_id)   ON DELETE CASCADE,
    CONSTRAINT fk_rev_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- ────────────────────────────────────────────────────────────
-- INDEXES for performance
-- ────────────────────────────────────────────────────────────
CREATE INDEX idx_orders_user      ON orders(user_id);
CREATE INDEX idx_orders_status    ON orders(status);
CREATE INDEX idx_orders_date      ON orders(order_date);
CREATE INDEX idx_deliveries_agent ON deliveries(agent_id);
CREATE INDEX idx_payments_status  ON payments(status);
CREATE INDEX idx_usub_user        ON user_subscriptions(user_id);
CREATE INDEX idx_usub_status      ON user_subscriptions(status);

-- ────────────────────────────────────────────────────────────
-- SEED DATA — sample records to test with
-- ────────────────────────────────────────────────────────────

-- Admin user (password: Admin@123 — bcrypt hash)
INSERT INTO users (full_name, email, password_hash, phone, role) VALUES
('Admin User',    'admin@tiffin.com',    '$2b$12$examplehashADMIN',    '9000000001', 'admin'),
('Riya Sharma',   'riya@example.com',    '$2b$12$examplehashCUST1',    '9000000002', 'customer'),
('Aman Verma',    'aman@example.com',    '$2b$12$examplehashCUST2',    '9000000003', 'customer'),
('Chef Mohan',    'mohan@tiffin.com',    '$2b$12$examplehashKITCH',    '9000000004', 'kitchen'),
('Ramesh Kumar',  'ramesh@tiffin.com',   '$2b$12$examplehashDELIV',    '9000000005', 'delivery');

-- Menu items
INSERT INTO menu_items (name, description, price, category) VALUES
('Dal Tadka + Rice',     'Yellow lentils tempered with cumin and ghee',  80.00,  'veg'),
('Paneer Butter Masala', 'Creamy tomato-based paneer curry',             120.00, 'veg'),
('Chicken Curry + Rice', 'Home-style chicken curry with steamed rice',   150.00, 'non-veg'),
('Aloo Sabzi + Roti',    '2 rotis with potato curry',                    70.00,  'veg'),
('Gulab Jamun (2pcs)',   'Classic sweet dessert',                        40.00,  'dessert'),
('Special Thali',        'Full meal: dal, sabzi, rice, roti, dessert',  200.00,  'special');

-- Subscription plans
INSERT INTO subscription_plans (plan_name, duration, price, description, meals_per_day) VALUES
('Daily Plan',   'daily',   80.00,  '1 meal per day, ordered daily',           1),
('Weekly Plan',  'weekly',  500.00, '1 meal/day for 7 days — save ₹60',        1),
('Monthly Plan', 'monthly', 1800.00,'1 meal/day for 30 days — save ₹600',      1),
('Premium Monthly','monthly',2500.00,'2 meals/day for 30 days',                2);

-- Delivery agent profile
INSERT INTO delivery_agents (user_id, vehicle_number) VALUES (5, 'UP14-AB-1234');