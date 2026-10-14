package com.example.db;

import java.util.Map;
import java.util.Objects;

/**
 * JDBC connection settings, read from environment variables so credentials stay out of source control.
 *
 * <ul>
 *   <li>{@code DB_URL} - e.g. {@code jdbc:mysql://localhost:3306/appdb}</li>
 *   <li>{@code DB_USER}</li>
 *   <li>{@code DB_PASSWORD}</li>
 * </ul>
 */
public record DatabaseConfig(String url, String user, String password) {

    public static final String DEFAULT_URL = "jdbc:mysql://localhost:3306/appdb";

    public DatabaseConfig {
        Objects.requireNonNull(url, "url");
        Objects.requireNonNull(user, "user");
        Objects.requireNonNull(password, "password");
    }

    public static DatabaseConfig fromEnvironment() {
        return fromMap(System.getenv());
    }

    static DatabaseConfig fromMap(Map<String, String> env) {
        String url = env.getOrDefault("DB_URL", DEFAULT_URL);
        String user = env.get("DB_USER");
        if (user == null || user.isBlank()) {
            throw new IllegalStateException("Environment variable DB_USER must be set");
        }
        String password = env.getOrDefault("DB_PASSWORD", "");
        return new DatabaseConfig(url, user, password);
    }

    @Override
    public String toString() {
        return "DatabaseConfig[url=" + url + ", user=" + user + ", password=****]";
    }
}
