-- =====================================================
-- Farm2Home Database Schema & Seed Data (MySQL)
-- =====================================================

CREATE DATABASE IF NOT EXISTS farm2home_db;
USE farm2home_db;

-- -----------------------------------------------------
-- Table `users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    role ENUM('user', 'farmer', 'admin') NOT NULL DEFAULT 'user',
    status ENUM('active', 'pending', 'suspended') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table `categories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table `products`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    stock INT NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table `orders`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address TEXT NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'Cash on Delivery',
    order_status ENUM('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table `order_items`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    farmer_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    status ENUM('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table `contact_messages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    subject VARCHAR(200),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- SAMPLE SEED DATA
-- Passwords below are pbkdf2:sha256 hashed for 'admin123', 'farmer123', 'user123'
-- Werkzeug compatible format
-- =====================================================

-- Insert Default Users
INSERT INTO users (id, full_name, email, password_hash, phone, address, role, status) VALUES
(1, 'System Admin', 'admin@farm2home.com', 'scrypt:32768:8:1$uH2GZ1bX8kP5Q2wR$c1dbf2ee960d70b777a83d73507df05ecb54ec6e1fa120531776db8a2305ca7ce257ef51a719eeeb2fa9ed019bb9e4695eb0ba8c91350a498b3fdf89aa165a2a', '1234567890', 'Farm2Home HQ, Green City', 'admin', 'active'),
(2, 'Ramesh Farmer', 'farmer@farm2home.com', 'scrypt:32768:8:1$uH2GZ1bX8kP5Q2wR$c1dbf2ee960d70b777a83d73507df05ecb54ec6e1fa120531776db8a2305ca7ce257ef51a719eeeb2fa9ed019bb9e4695eb0ba8c91350a498b3fdf89aa165a2a', '9876543210', 'Green Valley Farms, Sector 4', 'farmer', 'active'),
(3, 'John Buyer', 'user@farm2home.com', 'scrypt:32768:8:1$uH2GZ1bX8kP5Q2wR$c1dbf2ee960d70b777a83d73507df05ecb54ec6e1fa120531776db8a2305ca7ce257ef51a719eeeb2fa9ed019bb9e4695eb0ba8c91350a498b3fdf89aa165a2a', '9123456780', 'Flat 402, Sunshine Apartments', 'user', 'active')
ON DUPLICATE KEY UPDATE id=id;

-- Insert Categories
INSERT INTO categories (id, name, description, image_url) VALUES
(1, 'Fresh Vegetables', 'Organic and farm-fresh vegetables harvested daily.', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop'),
(2, 'Fresh Fruits', 'Naturally ripened seasonal fruits rich in nutrition.', 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=600&auto=format&fit=crop'),
(3, 'Dairy & Eggs', 'Pure farm milk, butter, cheese, and free-range eggs.', 'https://images.unsplash.com/photo-1528750997573-59b89d66f4f7?w=600&auto=format&fit=crop'),
(4, 'Grains & Pulses', 'Unpolished natural grains, wheat, rice, and pulses.', 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&auto=format&fit=crop'),
(5, 'Spices & Herbs', 'Aromatic handpicked spices and fresh garden herbs.', 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600&auto=format&fit=crop')
ON DUPLICATE KEY UPDATE id=id;

-- Insert Products
INSERT INTO products (id, farmer_id, category_id, title, description, price, unit, stock, image_url) VALUES
(1, 2, 1, 'Organic Tomatoes', 'Farm fresh vine-ripened red tomatoes without chemical pesticides.', 40.00, 'kg', 150, 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&auto=format&fit=crop'),
(2, 2, 1, 'Fresh Spinach (Palak)', 'Nutritious green spinach leaves freshly cut from the soil.', 25.00, 'bunch', 80, 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=600&auto=format&fit=crop'),
(3, 2, 2, 'Farm Apple Crisp', 'Sweet and juicy apples direct from Himalayan orchards.', 120.00, 'kg', 100, 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&auto=format&fit=crop'),
(4, 2, 3, 'Pure Cow Milk', 'Fresh unpasteurized whole cow milk delivered within hours of milking.', 60.00, 'liter', 50, 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=600&auto=format&fit=crop'),
(5, 2, 4, 'Organic Brown Rice', 'High fiber unpolished traditional brown rice.', 90.00, 'kg', 200, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop')
ON DUPLICATE KEY UPDATE id=id;

-- Insert Demo Order
INSERT INTO orders (id, user_id, total_amount, shipping_address, payment_method, order_status) VALUES
(1, 3, 160.00, 'Flat 402, Sunshine Apartments, Green City', 'Cash on Delivery', 'Shipped')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO order_items (id, order_id, product_id, farmer_id, quantity, price, status) VALUES
(1, 1, 1, 2, 2, 40.00, 'Shipped'),
(2, 1, 4, 2, 1, 60.00, 'Shipped')
ON DUPLICATE KEY UPDATE id=id;
