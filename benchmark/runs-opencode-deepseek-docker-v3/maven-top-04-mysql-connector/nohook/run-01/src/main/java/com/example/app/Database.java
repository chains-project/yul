package com.example.app;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

public final class Database {

    private final String url;
    private final String user;
    private final String password;

    public Database(String url, String user, String password) {
        this.url = url;
        this.user = user;
        this.password = password;
    }

    public static Database fromProperties(String resource) {
        Properties props = new Properties();
        try (InputStream in = Database.class.getClassLoader().getResourceAsStream(resource)) {
            if (in == null) {
                throw new IllegalStateException("Missing classpath resource: " + resource);
            }
            props.load(in);
        } catch (IOException e) {
            throw new IllegalStateException("Failed to load " + resource, e);
        }

        String url = envOrProperty("DB_URL", props, "db.url");
        String user = envOrProperty("DB_USER", props, "db.user");
        String password = envOrProperty("DB_PASSWORD", props, "db.password");
        return new Database(url, user, password);
    }

    private static String envOrProperty(String envName, Properties props, String propName) {
        String value = System.getenv(envName);
        return (value != null && !value.isBlank()) ? value : props.getProperty(propName);
    }

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }
}
