package com.example.db;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

class DatabaseConfigTest {

    @Test
    void readsAllValues() {
        DatabaseConfig config = DatabaseConfig.fromMap(Map.of(
                "DB_URL", "jdbc:mysql://db:3306/test",
                "DB_USER", "alice",
                "DB_PASSWORD", "secret"));

        assertEquals("jdbc:mysql://db:3306/test", config.url());
        assertEquals("alice", config.user());
        assertEquals("secret", config.password());
    }

    @Test
    void appliesDefaults() {
        DatabaseConfig config = DatabaseConfig.fromMap(Map.of("DB_USER", "alice"));

        assertEquals(DatabaseConfig.DEFAULT_URL, config.url());
        assertEquals("", config.password());
    }

    @Test
    void requiresUser() {
        assertThrows(IllegalStateException.class, () -> DatabaseConfig.fromMap(Map.of()));
    }

    @Test
    void toStringHidesPassword() {
        DatabaseConfig config = new DatabaseConfig("jdbc:mysql://x/y", "alice", "secret");

        assertFalse(config.toString().contains("secret"));
    }
}
