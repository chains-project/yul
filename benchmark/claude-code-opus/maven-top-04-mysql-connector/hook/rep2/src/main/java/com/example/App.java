package com.example;

import com.example.db.Database;
import com.example.db.DatabaseConfig;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;

public class App {

    public static void main(String[] args) {
        DatabaseConfig config = DatabaseConfig.load();
        System.out.println("Connecting with " + config);

        Database db = new Database(config);
        try {
            List<Map<String, Object>> rows = db.query(
                    "SELECT VERSION() AS version, DATABASE() AS current_db, NOW() AS server_time");
            rows.forEach(System.out::println);
        } catch (SQLException e) {
            System.err.println("Database error [SQLState " + e.getSQLState() + ", code "
                    + e.getErrorCode() + "]: " + e.getMessage());
            System.exit(1);
        }
    }
}
