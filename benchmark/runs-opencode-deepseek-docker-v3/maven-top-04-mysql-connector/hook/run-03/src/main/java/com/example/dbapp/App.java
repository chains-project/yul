package com.example.dbapp;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Properties;

public final class App {

    private static final String DEFAULT_QUERY = "SELECT NOW() AS server_time;";

    private App() {
    }

    public static void main(String[] args) {
        Properties config = loadConfig();

        String url = config.getProperty("db.url");
        String user = config.getProperty("db.user");
        String password = config.getProperty("db.password");
        String query = config.getProperty("db.query", DEFAULT_QUERY);

        try (Connection connection = DriverManager.getConnection(url, user, password);
             PreparedStatement statement = connection.prepareStatement(query);
             ResultSet results = statement.executeQuery()) {

            printResults(results);
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            System.exit(1);
        }
    }

    private static Properties loadConfig() {
        Properties config = new Properties();

        String url = System.getenv("DB_URL");
        String user = System.getenv("DB_USER");
        String password = System.getenv("DB_PASSWORD");
        String query = System.getenv("DB_QUERY");

        if (url == null) {
            url = "jdbc:mysql://localhost:3306/mysql";
        }
        if (user == null) {
            user = "root";
        }
        if (password == null) {
            password = "";
        }

        config.setProperty("db.url", url);
        config.setProperty("db.user", user);
        config.setProperty("db.password", password);
        if (query != null && !query.isBlank()) {
            config.setProperty("db.query", query);
        }
        return config;
    }

    private static void printResults(ResultSet results) throws SQLException {
        int columnCount = results.getMetaData().getColumnCount();
        while (results.next()) {
            StringBuilder row = new StringBuilder();
            for (int i = 1; i <= columnCount; i++) {
                if (i > 1) {
                    row.append(" | ");
                }
                row.append(results.getMetaData().getColumnLabel(i))
                        .append("=")
                        .append(results.getString(i));
            }
            System.out.println(row);
        }
    }
}
