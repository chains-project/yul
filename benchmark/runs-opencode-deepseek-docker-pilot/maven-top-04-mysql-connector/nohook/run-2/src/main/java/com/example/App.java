package com.example;

import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * Entry point demonstrating a MySQL connection and a few JDBC queries.
 */
public final class App {

    public static void main(String[] args) {
        DatabaseConfig config;
        try {
            config = DatabaseConfig.load();
        } catch (Exception e) {
            System.err.println("Failed to load database configuration: " + e.getMessage());
            System.exit(1);
            return;
        }

        try (Connection connection = config.getConnection()) {
            printServerInfo(connection);
            listTables(connection);
            userNameLookup(connection, args.length > 0 ? args[0] : "alice");
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static void printServerInfo(Connection connection) throws SQLException {
        DatabaseMetaData metaData = connection.getMetaData();
        System.out.printf("Connected to %s %s%n",
                metaData.getDatabaseProductName(),
                metaData.getDatabaseProductVersion());
        System.out.printf("Driver: %s %s%n",
                metaData.getDriverName(),
                metaData.getDriverVersion());
    }

    private static void listTables(Connection connection) throws SQLException {
        System.out.println("\nTables in current schema:");
        try (Statement statement = connection.createStatement();
             ResultSet rs = statement.executeQuery(
                     "SELECT table_name FROM information_schema.tables "
                             + "WHERE table_schema = DATABASE() ORDER BY table_name")) {
            boolean any = false;
            while (rs.next()) {
                any = true;
                System.out.println("  - " + rs.getString("table_name"));
            }
            if (!any) {
                System.out.println("  (none)");
            }
        }
    }

    private static void userNameLookup(Connection connection, String user) throws SQLException {
        String sql = "SELECT id, name FROM users WHERE name = ?";
        System.out.printf("%nLooking up user '%s' via prepared statement...%n", user);
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setString(1, user);
            try (ResultSet rs = statement.executeQuery()) {
                if (rs.next()) {
                    System.out.printf("  Found id=%d name=%s%n",
                            rs.getLong("id"), rs.getString("name"));
                } else {
                    System.out.println("  No matching user.");
                }
            }
        }
    }

    private App() {
    }
}
