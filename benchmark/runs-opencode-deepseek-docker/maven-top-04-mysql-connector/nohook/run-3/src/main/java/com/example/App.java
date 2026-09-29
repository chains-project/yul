package com.example;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class App {

    public static void main(String[] args) {
        String url = getenv("DB_URL", "jdbc:mysql://localhost:3306/demo?useSSL=false&serverTimezone=UTC");
        String user = getenv("DB_USER", "root");
        String password = getenv("DB_PASSWORD", "");

        String sql = args.length > 0 ? args[0] : "SELECT VERSION() AS version";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            int columns = rs.getMetaData().getColumnCount();
            while (rs.next()) {
                StringBuilder row = new StringBuilder();
                for (int i = 1; i <= columns; i++) {
                    if (i > 1) {
                        row.append(" | ");
                    }
                    row.append(rs.getString(i));
                }
                System.out.println(row);
            }
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static String getenv(String name, String fallback) {
        String value = System.getenv(name);
        return value == null || value.isBlank() ? fallback : value;
    }
}
