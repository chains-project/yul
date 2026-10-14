package com.example.db;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.Map;
import java.util.Properties;

/**
 * JDBC connection settings. Resolution order for each key:
 * system property, then environment variable, then {@code db.properties} on the classpath.
 */
public record DatabaseConfig(String url, String user, String password) {

    private static final String RESOURCE = "/db.properties";

    public static DatabaseConfig load() {
        return load(System.getenv(), System.getProperties(), loadDefaults());
    }

    static DatabaseConfig load(Map<String, String> env, Properties sysProps, Properties defaults) {
        String url = resolve("db.url", "DB_URL", env, sysProps, defaults);
        if (url == null || url.isBlank()) {
            throw new IllegalStateException("No database URL configured (set DB_URL or db.url)");
        }
        return new DatabaseConfig(
                url,
                resolve("db.user", "DB_USER", env, sysProps, defaults),
                resolve("db.password", "DB_PASSWORD", env, sysProps, defaults));
    }

    private static String resolve(String key, String envKey, Map<String, String> env,
                                  Properties sysProps, Properties defaults) {
        String value = sysProps.getProperty(key);
        if (value == null) value = env.get(envKey);
        if (value == null) value = defaults.getProperty(key);
        return value;
    }

    private static Properties loadDefaults() {
        Properties props = new Properties();
        try (InputStream in = DatabaseConfig.class.getResourceAsStream(RESOURCE)) {
            if (in != null) props.load(in);
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to read " + RESOURCE, e);
        }
        return props;
    }

    @Override
    public String toString() {
        return "DatabaseConfig[url=" + url + ", user=" + user + ", password=****]";
    }
}
