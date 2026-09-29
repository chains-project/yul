package com.example.dbapp;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

/**
 * Loads JDBC settings from {@code db.properties} (or environment/system
 * overrides) and hands out connections.
 */
public final class Database {

    private static final String CONFIG_FILE = "db.properties";

    private final String url;
    private final String user;
    private final String password;

    public Database(Properties config) {
        this.url = require(config, "db.url");
        this.user = require(config, "db.user");
        this.password = require(config, "db.password");
    }

    public static Database fromConfig() {
        return new Database(loadConfig());
    }

    public static Properties loadConfig() {
        Properties props = new Properties();
        try (InputStream in = Database.class.getClassLoader().getResourceAsStream(CONFIG_FILE)) {
            if (in != null) {
                props.load(in);
            }
        } catch (IOException e) {
            throw new IllegalStateException("Failed to read " + CONFIG_FILE, e);
        }

        // Environment variables / -D system properties override bundled defaults.
        applyOverride(props, "db.url", "DB_URL");
        applyOverride(props, "db.user", "DB_USER");
        applyOverride(props, "db.password", "DB_PASSWORD");
        return props;
    }

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }

    private static void applyOverride(Properties props, String key, String envVar) {
        String value = System.getProperty(key);
        if (value == null || value.isBlank()) {
            value = System.getenv(envVar);
        }
        if (value != null && !value.isBlank()) {
            props.setProperty(key, value);
        }
    }

    private static String require(Properties props, String key) {
        String value = props.getProperty(key);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException("Missing required database setting: " + key);
        }
        return value;
    }
}
