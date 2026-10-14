package com.example.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/** Opens JDBC connections. Callers own the returned connection and must close it. */
public final class Database {

    private final DatabaseConfig config;

    public Database(DatabaseConfig config) {
        this.config = config;
    }

    public Connection getConnection() throws SQLException {
        // The MySQL driver registers itself via the JDBC ServiceLoader mechanism; no Class.forName needed.
        return DriverManager.getConnection(config.url(), config.user(), config.password());
    }
}
