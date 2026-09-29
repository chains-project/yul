CREATE DATABASE IF NOT EXISTS demo;
USE demo;

CREATE TABLE IF NOT EXISTS customers (
    id    BIGINT       NOT NULL AUTO_INCREMENT,
    name  VARCHAR(120) NOT NULL,
    email VARCHAR(180) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_customers_email (email)
);

INSERT INTO customers (name, email) VALUES
    ('Ada Lovelace', 'ada@example.com'),
    ('Grace Hopper', 'grace@example.com')
ON DUPLICATE KEY UPDATE name = VALUES(name);
