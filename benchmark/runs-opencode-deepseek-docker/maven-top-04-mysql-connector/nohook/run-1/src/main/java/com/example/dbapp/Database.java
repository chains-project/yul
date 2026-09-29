package com.example.dbapp;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public final class Database {

    private final DatabaseConfig config;

    public Database(DatabaseConfig config) {
        this.config = config;
    }

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(config.url(), config.user(), config.password());
    }

    public DatabaseConfig config() {
        return config;
    }
}
