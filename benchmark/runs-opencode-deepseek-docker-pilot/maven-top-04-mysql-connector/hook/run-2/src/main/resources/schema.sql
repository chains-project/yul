CREATE DATABASE IF NOT EXISTS demo;

USE demo;

CREATE TABLE IF NOT EXISTS customers (
    id    BIGINT       NOT NULL AUTO_INCREMENT,
    name  VARCHAR(120) NOT NULL,
    email VARCHAR(190) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_customers_email (email)
);

INSERT IGNORE INTO customers (name, email) VALUES
    ('Ada Lovelace', 'ada@example.com'),
    ('Grace Hopper', 'grace@example.com');
