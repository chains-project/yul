package com.example;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

/**
 * Loads JDBC settings and opens MySQL connections.
 *
 * <p>Values are resolved in this order: environment variables
 * ({@code DB_URL}, {@code DB_USER}, {@code DB_PASSWORD}), then the bundled
 * {@code db.properties} classpath resource.</p>
 */
public final class Database {

    private static final String DEFAULT_RESOURCE = "/db.properties";

    private final String url;
    private final String user;
    private final String password;

    public Database(String url, String user, String password) {
        this.url = url;
        this.user = user;
        this.password = password;
    }

    public static Database fromClasspath() {
        return fromClasspath(DEFAULT_RESOURCE);
    }

    public static Database fromClasspath(String resource) {
        Properties properties = new Properties();
        try (InputStream input = Database.class.getResourceAsStream(resource)) {
            if (input == null) {
                throw new IllegalStateException("JDBC config not found on classpath: " + resource);
            }
            properties.load(input);
        } catch (IOException e) {
            throw new IllegalStateException("Unable to read JDBC config: " + resource, e);
        }

        String url = envOrDefault("DB_URL", properties.getProperty("db.url"));
        String user = envOrDefault("DB_USER", properties.getProperty("db.user"));
        String password = envOrDefault("DB_PASSWORD", properties.getProperty("db.password", ""));

        if (url == null || url.isBlank()) {
            throw new IllegalStateException("No JDBC URL configured (db.url or DB_URL)");
        }
        return new Database(url, user, password);
    }

    private static String envOrDefault(String envName, String fallback) {
        String value = System.getenv(envName);
        return (value == null || value.isBlank()) ? fallback : value;
    }

    public Connection connect() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }
}
