package com.example.db;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.Properties;

/**
 * JDBC connection settings. Values come from {@code db.properties} on the classpath
 * and can be overridden by the environment variables DB_URL, DB_USER and DB_PASSWORD.
 */
public record DatabaseConfig(String url, String user, String password) {

    public static DatabaseConfig load() {
        Properties props = new Properties();
        try (InputStream in = DatabaseConfig.class.getResourceAsStream("/db.properties")) {
            if (in != null) {
                props.load(in);
            }
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to read db.properties", e);
        }
        return new DatabaseConfig(
                setting("DB_URL", props.getProperty("db.url")),
                setting("DB_USER", props.getProperty("db.user")),
                setting("DB_PASSWORD", props.getProperty("db.password", "")));
    }

    private static String setting(String envVar, String fallback) {
        String value = System.getenv(envVar);
        if (value != null && !value.isBlank()) {
            return value;
        }
        if (fallback == null) {
            throw new IllegalStateException("Missing DB setting: set " + envVar + " or the matching key in db.properties");
        }
        return fallback;
    }

    @Override
    public String toString() {
        return "DatabaseConfig[url=" + url + ", user=" + user + ", password=***]";
    }
}
