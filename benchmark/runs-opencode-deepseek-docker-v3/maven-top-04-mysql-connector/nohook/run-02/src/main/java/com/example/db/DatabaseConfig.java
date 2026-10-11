package com.example.db;

/**
 * Connection settings, resolved from environment variables so that credentials
 * are never hard-coded in the source tree.
 */
public record DatabaseConfig(String url, String username, String password) {

    public static DatabaseConfig fromEnvironment() {
        String host = env("DB_HOST", "localhost");
        String port = env("DB_PORT", "3306");
        String database = env("DB_NAME", "appdb");

        String url = "jdbc:mysql://" + host + ":" + port + "/" + database
                + "?useSSL=false"
                + "&serverTimezone=UTC"
                + "&allowPublicKeyRetrieval=true";

        return new DatabaseConfig(
                url,
                env("DB_USER", "root"),
                env("DB_PASSWORD", ""));
    }

    private static String env(String key, String fallback) {
        String value = System.getenv(key);
        return (value == null || value.isBlank()) ? fallback : value;
    }
}
