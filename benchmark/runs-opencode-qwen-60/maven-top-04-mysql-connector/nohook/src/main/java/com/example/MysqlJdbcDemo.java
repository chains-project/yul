package com.example;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MysqlJdbcDemo {

    private final String url;
    private final String username;
    private final String password;

    public MysqlJdbcDemo(String url, String username, String password) {
        this.url = url;
        this.username = username;
        this.password = password;
    }

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url, username, password);
    }

    public List<Map<String, Object>> query(String sql) throws SQLException {
        List<Map<String, Object>> results = new ArrayList<>();
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql);
             ResultSet rs = stmt.executeQuery()) {

            int columnCount = rs.getMetaData().getColumnCount();
            String[] columnNames = new String[columnCount];
            for (int i = 1; i <= columnCount; i++) {
                columnNames[i - 1] = rs.getMetaData().getColumnLabel(i);
            }

            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                for (int i = 0; i < columnCount; i++) {
                    row.put(columnNames[i], rs.getObject(i + 1));
                }
                results.add(row);
            }
        }
        return results;
    }

    public int update(String sql, Object... params) throws SQLException {
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            for (int i = 0; i < params.length; i++) {
                stmt.setObject(i + 1, params[i]);
            }
            return stmt.executeUpdate();
        }
    }

    public void close() {
        // No persistent state to close
    }

    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/testdb?useSSL=false&serverTimezone=UTC";
        String username = "root";
        String password = "password";

        MysqlJdbcDemo demo = new MysqlJdbcDemo(url, username, password);

        try {
            // Test connection
            try (Connection conn = demo.getConnection()) {
                System.out.println("Connected to MySQL: " + conn.getCatalog());
            }

            // Create a demo table
            demo.update(
                "CREATE TABLE IF NOT EXISTS users ("
                + "id INT AUTO_INCREMENT PRIMARY KEY,"
                + "name VARCHAR(100),"
                + "email VARCHAR(100))"
            );

            // Insert test data
            demo.update("INSERT INTO users (name, email) VALUES (?, ?)", "Alice", "alice@example.com");
            demo.update("INSERT INTO users (name, email) VALUES (?, ?)", "Bob", "bob@example.com");

            // Query data
            List<Map<String, Object>> rows = demo.query("SELECT * FROM users");
            System.out.println("\nUsers:");
            for (Map<String, Object> row : rows) {
                System.out.println(row);
            }

        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}