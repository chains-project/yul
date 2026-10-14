package com.example.db;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.Map;
import java.util.Properties;

/**
 * Connection settings resolved in priority order:
 * system property, environment variable, then {@code db.properties} on the classpath.
 */
public record DbConfig(String url, String user, String password) {

    public static DbConfig load() {
        return load(System.getenv(), System.getProperties(), loadDefaults());
    }

    static DbConfig load(Map<String, String> env, Properties sysProps, Properties defaults) {
        return new DbConfig(
                resolve("db.url", "DB_URL", env, sysProps, defaults, true),
                resolve("db.user", "DB_USER", env, sysProps, defaults, true),
                resolve("db.password", "DB_PASSWORD", env, sysProps, defaults, false));
    }

    private static String resolve(String key, String envKey, Map<String, String> env,
                                  Properties sysProps, Properties defaults, boolean required) {
        String value = sysProps.getProperty(key);
        if (value == null) {
            value = env.get(envKey);
        }
        if (value == null) {
            value = defaults.getProperty(key);
        }
        if (value == null && required) {
            throw new IllegalStateException("Missing database setting: " + key + " / " + envKey);
        }
        return value == null ? "" : value;
    }

    private static Properties loadDefaults() {
        Properties props = new Properties();
        try (InputStream in = DbConfig.class.getResourceAsStream("/db.properties")) {
            if (in != null) {
                props.load(in);
            }
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to read db.properties", e);
        }
        return props;
    }

    @Override
    public String toString() {
        return "DbConfig[url=" + url + ", user=" + user + ", password=****]";
    }
}
