package com.example.dbapp;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public final class DatabaseConfig {

    private static final String DEFAULT_RESOURCE = "db.properties";
    private static final String DEFAULT_URL =
            "jdbc:mysql://localhost:3306/demo?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true";
    private static final String DEFAULT_USER = "root";
    private static final String DEFAULT_PASSWORD = "";

    private final String url;
    private final String user;
    private final String password;

    public DatabaseConfig(String url, String user, String password) {
        this.url = requireNonBlank(url, "url");
        this.user = user == null ? "" : user;
        this.password = password == null ? "" : password;
    }

    public static DatabaseConfig load() {
        return load(DEFAULT_RESOURCE);
    }

    public static DatabaseConfig load(String resource) {
        Properties properties = new Properties();
        try (InputStream in = DatabaseConfig.class.getClassLoader().getResourceAsStream(resource)) {
            if (in != null) {
                properties.load(in);
            }
        } catch (IOException e) {
            throw new IllegalStateException("Unable to read " + resource, e);
        }

        String url = firstNonBlank(System.getenv("DB_URL"), properties.getProperty("db.url"), DEFAULT_URL);
        String user = firstNonBlank(System.getenv("DB_USER"), properties.getProperty("db.user"), DEFAULT_USER);
        String password = firstNonBlank(System.getenv("DB_PASSWORD"), properties.getProperty("db.password"), DEFAULT_PASSWORD);
        return new DatabaseConfig(url, user, password);
    }

    public String url() {
        return url;
    }

    public String user() {
        return user;
    }

    public String password() {
        return password;
    }

    private static String requireNonBlank(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must not be blank");
        }
        return value;
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }
}
