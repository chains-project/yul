package com.example.db;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.Map;
import java.util.Properties;

/**
 * Connection settings loaded from {@code db.properties} on the classpath,
 * with environment variables (DB_URL, DB_USER, DB_PASSWORD) taking precedence.
 */
public record DatabaseConfig(String url, String user, String password) {

    private static final String RESOURCE = "/db.properties";

    public static DatabaseConfig load() {
        return load(System.getenv());
    }

    static DatabaseConfig load(Map<String, String> env) {
        Properties props = new Properties();
        try (InputStream in = DatabaseConfig.class.getResourceAsStream(RESOURCE)) {
            if (in != null) {
                props.load(in);
            }
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to read " + RESOURCE, e);
        }

        String url = env.getOrDefault("DB_URL", props.getProperty("db.url"));
        String user = env.getOrDefault("DB_USER", props.getProperty("db.user"));
        String password = env.getOrDefault("DB_PASSWORD", props.getProperty("db.password", ""));

        if (url == null || url.isBlank()) {
            throw new IllegalStateException("No database URL configured (set DB_URL or db.url)");
        }
        return new DatabaseConfig(url, user, password);
    }

    @Override
    public String toString() {
        return "DatabaseConfig[url=" + url + ", user=" + user + ", password=****]";
    }
}
