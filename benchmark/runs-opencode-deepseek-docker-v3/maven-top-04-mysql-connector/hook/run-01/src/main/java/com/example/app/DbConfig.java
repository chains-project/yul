package com.example.app;

public record DbConfig(String host, int port, String database, String user, String password) {

    public static DbConfig fromEnvironment() {
        String host = env("DB_HOST", "localhost");
        int port = Integer.parseInt(env("DB_PORT", "3306"));
        String database = env("DB_NAME", "test");
        String user = env("DB_USER", "root");
        String password = env("DB_PASSWORD", "");
        return new DbConfig(host, port, database, user, password);
    }

    public String jdbcUrl() {
        return "jdbc:mysql://" + host + ":" + port + "/" + database
                + "?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC";
    }

    private static String env(String name, String defaultValue) {
        String value = System.getenv(name);
        return (value == null || value.isBlank()) ? defaultValue : value;
    }
}
