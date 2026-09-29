-- Sample schema used by the demo. Run once against your database:
--   mysql -u root -p mydb < schema.sql

CREATE TABLE IF NOT EXISTS users (
    id   BIGINT       NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_users_name (name)
);

INSERT IGNORE INTO users (name) VALUES ('alice'), ('bob');
