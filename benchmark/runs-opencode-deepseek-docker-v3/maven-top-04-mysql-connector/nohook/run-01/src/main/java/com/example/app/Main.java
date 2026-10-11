package com.example.app;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public final class Main {

    public static void main(String[] args) {
        Database database = Database.fromProperties("db.properties");

        try (Connection connection = database.getConnection()) {
            System.out.println("Connected to " + connection.getMetaData().getURL());

            String sql = "SELECT id, name FROM users WHERE name LIKE ? ORDER BY id";
            List<String> rows = search(connection, sql, "%");

            System.out.println("Rows found: " + rows.size());
            rows.forEach(row -> System.out.println(" - " + row));
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace(System.err);
            System.exit(1);
        }
    }

    static List<String> search(Connection connection, String sql, String namePattern) throws SQLException {
        List<String> results = new ArrayList<>();
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setString(1, namePattern);
            try (ResultSet rs = statement.executeQuery()) {
                while (rs.next()) {
                    results.add(rs.getLong("id") + ": " + rs.getString("name"));
                }
            }
        }
        return results;
    }
}
