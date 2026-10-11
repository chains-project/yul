package com.example.jdbc;

import java.io.IOException;
import java.io.InputStream;
import java.util.Objects;
import java.util.Properties;

/**
 * Loads database connection settings from {@code db.properties} on the classpath,
 * allowing environment variables (DB_URL, DB_USER, DB_PASSWORD) to override them.
 */
public final class DbConfig {

    private final String url;
    private final String username;
    private final String password;

    private DbConfig(String url, String username, String password) {
        this.url = Objects.requireNonNull(url, "url");
        this.username = Objects.requireNonNull(username, "username");
        this.password = Objects.requireNonNull(password, "password");
    }

    /** Creates a config programmatically, mainly for tests. */
    public static DbConfig of(String url, String username, String password) {
        return new DbConfig(url, username, password);
    }

    public static DbConfig load() {
        Properties props = new Properties();
        try (InputStream in = DbConfig.class.getResourceAsStream("/db.properties")) {
            if (in == null) {
                throw new IllegalStateException("db.properties not found on the classpath");
            }
            props.load(in);
        } catch (IOException e) {
            throw new IllegalStateException("Failed to load db.properties", e);
        }

        String url = envOrDefault("DB_URL", props.getProperty("db.url"));
        String username = envOrDefault("DB_USER", props.getProperty("db.username"));
        String password = envOrDefault("DB_PASSWORD", props.getProperty("db.password"));

        return new DbConfig(url, username, password);
    }

    private static String envOrDefault(String envVar, String fallback) {
        String value = System.getenv(envVar);
        return (value != null && !value.isBlank()) ? value : fallback;
    }

    public String url() {
        return url;
    }

    public String username() {
        return username;
    }

    public String password() {
        return password;
    }
}
