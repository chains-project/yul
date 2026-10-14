package com.example.db;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

class DatabaseConfigTest {

    @Test
    void usesPropertiesFileByDefault() {
        DatabaseConfig config = DatabaseConfig.load(Map.of());
        assertEquals("jdbc:mysql://localhost:3306/mydb?sslMode=PREFERRED&serverTimezone=UTC", config.url());
        assertEquals("root", config.user());
    }

    @Test
    void environmentOverridesProperties() {
        DatabaseConfig config = DatabaseConfig.load(Map.of(
                "DB_URL", "jdbc:mysql://db.internal:3306/app",
                "DB_USER", "app",
                "DB_PASSWORD", "secret"));
        assertEquals("jdbc:mysql://db.internal:3306/app", config.url());
        assertEquals("app", config.user());
        assertEquals("secret", config.password());
    }

    @Test
    void toStringMasksPassword() {
        DatabaseConfig config = new DatabaseConfig("jdbc:mysql://x/y", "u", "secret");
        assertFalse(config.toString().contains("secret"));
    }
}
