package com.example.db;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;

public class App {

    public static void main(String[] args) {
        DbConfig config = DbConfig.load();
        System.out.println("Connecting with " + config);
        Database db = new Database(config);

        try {
            List<Map<String, Object>> info = db.query("SELECT VERSION() AS version, DATABASE() AS db");
            System.out.println("Connected: " + info.getFirst());

            String sql = args.length > 0 ? String.join(" ", args) : "SHOW TABLES";
            System.out.println("> " + sql);
            for (Map<String, Object> row : db.query(sql)) {
                System.out.println(row);
            }
        } catch (SQLException e) {
            System.err.println("Database error [" + e.getSQLState() + "]: " + e.getMessage());
            System.exit(1);
        }
    }
}
