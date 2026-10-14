package com.example.db;

import java.sql.SQLException;
import java.util.List;

public class App {

    public static void main(String[] args) {
        DatabaseConfig config = DatabaseConfig.load();
        System.out.println("Connecting with " + config);

        Database db = new Database(config);
        try {
            List<String> rows = db.query(
                    "SELECT VERSION() AS version, DATABASE() AS db_name",
                    rs -> "MySQL " + rs.getString("version") + ", database: " + rs.getString("db_name"));
            rows.forEach(System.out::println);
        } catch (SQLException e) {
            System.err.println("Database error [" + e.getSQLState() + "]: " + e.getMessage());
            System.exit(1);
        }
    }
}
