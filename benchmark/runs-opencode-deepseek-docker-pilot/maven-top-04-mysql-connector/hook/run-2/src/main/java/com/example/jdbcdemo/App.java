package com.example.jdbcdemo;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;

public final class App {

    private static final String DEFAULT_QUERY =
            "SELECT id, name, email FROM customers ORDER BY id";

    private App() {
    }

    public static void main(String[] args) throws Exception {
        Properties config = Database.loadConfig();
        Database database = new Database(config);
        String sql = args.length > 0 ? args[0] : DEFAULT_QUERY;

        System.out.println("Connecting to " + database.getUrl());
        try (Connection connection = database.getConnection();
             Statement statement = connection.createStatement();
             ResultSet results = statement.executeQuery(sql)) {
            print(results);
        }
    }

    private static void print(ResultSet results) throws SQLException {
        ResultSetMetaData meta = results.getMetaData();
        int columnCount = meta.getColumnCount();

        StringBuilder header = new StringBuilder();
        for (int i = 1; i <= columnCount; i++) {
            if (i > 1) {
                header.append(" | ");
            }
            header.append(meta.getColumnLabel(i));
        }
        System.out.println(header);

        int rowCount = 0;
        while (results.next()) {
            StringBuilder row = new StringBuilder();
            for (int i = 1; i <= columnCount; i++) {
                if (i > 1) {
                    row.append(" | ");
                }
                row.append(results.getString(i));
            }
            System.out.println(row);
            rowCount++;
        }
        System.out.println("(" + rowCount + " row" + (rowCount == 1 ? "" : "s") + ")");
    }
}
