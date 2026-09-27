package com.example.dbapp;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class DatabaseConfigTest {

    @Test
    void exposesConfiguredValues() {
        DatabaseConfig config = new DatabaseConfig("jdbc:mysql://host:3306/db", "user", "secret");

        assertEquals("jdbc:mysql://host:3306/db", config.url());
        assertEquals("user", config.user());
        assertEquals("secret", config.password());
    }

    @Test
    void normalizesNullUserAndPasswordToEmpty() {
        DatabaseConfig config = new DatabaseConfig("jdbc:mysql://host:3306/db", null, null);

        assertEquals("", config.user());
        assertEquals("", config.password());
    }

    @Test
    void rejectsBlankUrl() {
        assertThrows(IllegalArgumentException.class,
                () -> new DatabaseConfig("  ", "user", "secret"));
    }

    @Test
    void loadProducesUsableConfiguration() {
        DatabaseConfig config = DatabaseConfig.load();

        assertNotNull(config);
        assertFalse(config.url().isBlank());
    }
}
