package com.example.db;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.sql.Driver;
import java.sql.DriverManager;
import java.util.Collections;
import org.junit.jupiter.api.Test;

class DatabaseConfigTest {

    @Test
    void loadsDefaultsFromClasspath() {
        DatabaseConfig config = DatabaseConfig.load();
        if (System.getenv("DB_URL") == null) {
            assertTrue(config.url().startsWith("jdbc:mysql://"));
        }
    }

    @Test
    void toStringMasksPassword() {
        DatabaseConfig config = new DatabaseConfig("jdbc:mysql://h/db", "u", "secret");
        assertFalse(config.toString().contains("secret"));
    }

    @Test
    void mysqlDriverIsOnClasspath() {
        boolean found = Collections.list(DriverManager.getDrivers()).stream()
                .map(Driver::getClass)
                .map(Class::getName)
                .anyMatch(name -> name.equals("com.mysql.cj.jdbc.Driver"));
        assertTrue(found, "com.mysql.cj.jdbc.Driver not registered");
    }
}
