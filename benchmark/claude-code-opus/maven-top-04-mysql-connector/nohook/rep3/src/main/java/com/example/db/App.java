package com.example.db;

import java.sql.SQLException;
import java.util.List;

/** Connects to MySQL, prints the server version, and lists tables in the current schema. */
public class App {

    public static void main(String[] args) {
        DatabaseConfig config = DatabaseConfig.fromEnvironment();
        Database db = new Database(config);
        System.out.println("Connecting with " + config);

        try {
            String version = db.query("SELECT VERSION()", rs -> rs.getString(1)).getFirst();
            System.out.println("MySQL server version: " + version);

            List<String> tables = db.query(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE() ORDER BY table_name",
                    rs -> rs.getString(1));
            System.out.println("Tables in current schema (" + tables.size() + "):");
            tables.forEach(t -> System.out.println("  " + t));
        } catch (SQLException e) {
            System.err.println("Database error [" + e.getSQLState() + "]: " + e.getMessage());
            System.exit(1);
        }
    }
}
