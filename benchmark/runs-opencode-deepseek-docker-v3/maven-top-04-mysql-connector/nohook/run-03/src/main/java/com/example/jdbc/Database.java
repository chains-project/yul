package com.example.jdbc;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Owns JDBC connections for the application. The MySQL driver is loaded
 * explicitly so the code also works with older servlet containers that do
 * not discover JDBC 4.0 service providers automatically.
 */
public final class Database implements AutoCloseable {

    static {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            throw new ExceptionInInitializerError(
                    "MySQL JDBC driver not on the classpath: " + e.getMessage());
        }
    }

    private final DbConfig config;

    public Database(DbConfig config) {
        this.config = config;
    }

    public Connection connect() throws SQLException {
        return DriverManager.getConnection(config.url(), config.username(), config.password());
    }

    @Override
    public void close() {
        // No pooled resources to release; DriverManager connections are
        // closed individually by callers via try-with-resources.
    }
}
