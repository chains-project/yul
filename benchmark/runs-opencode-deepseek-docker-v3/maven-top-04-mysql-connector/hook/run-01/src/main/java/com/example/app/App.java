package com.example.app;

import java.sql.SQLException;
import java.util.List;

public final class App {

    public static void main(String[] args) {
        DbConfig config = DbConfig.fromEnvironment();

        try (Database database = Database.connect(config)) {
            List<String> tables = database.listTables();
            System.out.println("Connected to " + config.jdbcUrl());
            System.out.println("Tables:");
            tables.forEach(table -> System.out.println("  - " + table));

            if (args.length > 0) {
                String sql = String.join(" ", args);
                System.out.println();
                System.out.println("Query: " + sql);
                List<String> rows = database.query(sql);
                rows.forEach(row -> System.out.println("  " + row));
            }
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            System.exit(1);
        }
    }
}
