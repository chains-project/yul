-- Sample schema matching the default query in App.java.
-- Run with: mysql -u root -p < schema.sql
CREATE DATABASE IF NOT EXISTS demo;
USE demo;

CREATE TABLE IF NOT EXISTS users (
    id    BIGINT       NOT NULL AUTO_INCREMENT,
    name  VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email)
);

INSERT INTO users (name, email) VALUES
    ('Ada Lovelace',  'ada@example.com'),
    ('Alan Turing',   'alan@example.com'),
    ('Grace Hopper',  'grace@example.com')
ON DUPLICATE KEY UPDATE name = VALUES(name);
