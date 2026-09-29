package com.example.jdbcdemo;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

public final class Database {

    private static final String CONFIG_RESOURCE = "db.properties";

    private final String url;
    private final String user;
    private final String password;

    public Database(Properties config) {
        this.url = resolve(config, "db.url", "DB_URL");
        this.user = resolve(config, "db.user", "DB_USER");
        this.password = resolve(config, "db.password", "DB_PASSWORD");
    }

    public static Properties loadConfig() throws IOException {
        Properties properties = new Properties();
        try (InputStream input = Database.class.getClassLoader().getResourceAsStream(CONFIG_RESOURCE)) {
            if (input != null) {
                properties.load(input);
            }
        }
        return properties;
    }

    private static String resolve(Properties config, String propertyKey, String envKey) {
        String envValue = System.getenv(envKey);
        if (envValue != null && !envValue.isBlank()) {
            return envValue.trim();
        }
        String propertyValue = config.getProperty(propertyKey);
        if (propertyValue == null || propertyValue.isBlank()) {
            throw new IllegalStateException(
                    "Missing database setting '" + propertyKey + "'. Set it in " + CONFIG_RESOURCE
                            + " or via the " + envKey + " environment variable.");
        }
        return propertyValue.trim();
    }

    public String getUrl() {
        return url;
    }

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }
}
