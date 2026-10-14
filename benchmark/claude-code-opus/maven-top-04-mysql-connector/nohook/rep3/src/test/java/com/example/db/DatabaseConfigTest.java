package com.example.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import java.sql.Driver;
import java.sql.DriverManager;
import java.util.Map;
import org.junit.jupiter.api.Test;

class DatabaseConfigTest {

    @Test
    void usesDefaultsWhenUnset() {
        DatabaseConfig config = DatabaseConfig.fromMap(Map.of());
        assertEquals(DatabaseConfig.DEFAULT_URL, config.url());
        assertEquals(DatabaseConfig.DEFAULT_USER, config.user());
        assertEquals("", config.password());
    }

    @Test
    void readsValuesFromEnvironment() {
        DatabaseConfig config = DatabaseConfig.fromMap(Map.of(
                "DB_URL", "jdbc:mysql://db:3306/app",
                "DB_USER", "app",
                "DB_PASSWORD", "secret"));
        assertEquals("jdbc:mysql://db:3306/app", config.url());
        assertEquals("app", config.user());
        assertEquals("secret", config.password());
    }

    @Test
    void toStringMasksPassword() {
        DatabaseConfig config = new DatabaseConfig("jdbc:mysql://h/db", "u", "secret");
        assertFalse(config.toString().contains("secret"));
    }

    @Test
    void mysqlDriverIsOnClasspath() throws Exception {
        Driver driver = DriverManager.getDriver("jdbc:mysql://localhost:3306/test");
        assertEquals("com.mysql.cj.jdbc.Driver", driver.getClass().getName());
    }
}
