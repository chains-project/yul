package com.example;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

/**
 * Loads connection settings and hands out JDBC connections.
 *
 * <p>Settings are read from {@code db.properties} on the classpath and may be
 * overridden with the {@code DB_URL}, {@code DB_USER} and {@code DB_PASSWORD}
 * environment variables.</p>
 */
public final class DatabaseConfig {

    private final String url;
    private final String user;
    private final String password;

    private DatabaseConfig(String url, String user, String password) {
        this.url = url;
        this.user = user;
        this.password = password;
    }

    public static DatabaseConfig load() throws IOException {
        Properties props = new Properties();
        try (InputStream in = DatabaseConfig.class.getResourceAsStream("/db.properties")) {
            if (in == null) {
                throw new IOException("db.properties not found on the classpath");
            }
            props.load(in);
        }

        String url = envOrDefault("DB_URL", props.getProperty("db.url"));
        String user = envOrDefault("DB_USER", props.getProperty("db.user"));
        String password = envOrDefault("DB_PASSWORD", props.getProperty("db.password"));

        if (url == null || url.isBlank()) {
            throw new IOException("Database URL is not configured (db.url / DB_URL)");
        }
        return new DatabaseConfig(url, user, password);
    }

    private static String envOrDefault(String name, String fallback) {
        String value = System.getenv(name);
        return (value == null || value.isBlank()) ? fallback : value;
    }

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }

    public String getUrl() {
        return url;
    }
}
