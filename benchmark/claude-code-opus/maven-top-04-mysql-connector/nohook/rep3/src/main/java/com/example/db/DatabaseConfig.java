package com.example.db;

import java.util.Map;
import java.util.Objects;

/**
 * Connection settings for MySQL, read from environment variables.
 *
 * <ul>
 *   <li>{@code DB_URL} – JDBC URL (default {@code jdbc:mysql://localhost:3306/test})</li>
 *   <li>{@code DB_USER} – user name (default {@code root})</li>
 *   <li>{@code DB_PASSWORD} – password (default empty)</li>
 * </ul>
 */
public record DatabaseConfig(String url, String user, String password) {

    static final String DEFAULT_URL = "jdbc:mysql://localhost:3306/test";
    static final String DEFAULT_USER = "root";

    public DatabaseConfig {
        Objects.requireNonNull(url, "url");
        Objects.requireNonNull(user, "user");
        Objects.requireNonNull(password, "password");
    }

    public static DatabaseConfig fromEnvironment() {
        return fromMap(System.getenv());
    }

    static DatabaseConfig fromMap(Map<String, String> env) {
        return new DatabaseConfig(
                env.getOrDefault("DB_URL", DEFAULT_URL),
                env.getOrDefault("DB_USER", DEFAULT_USER),
                env.getOrDefault("DB_PASSWORD", ""));
    }

    @Override
    public String toString() {
        return "DatabaseConfig[url=" + url + ", user=" + user + ", password=****]";
    }
}
