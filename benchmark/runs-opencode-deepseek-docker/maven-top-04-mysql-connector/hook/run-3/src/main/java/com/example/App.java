package com.example;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.StringJoiner;

/**
 * Connects to MySQL over JDBC and runs a query.
 *
 * <p>Usage: {@code mvn exec:java -Dexec.args="SELECT * FROM users"}.
 * Without arguments a simple {@code SELECT 1} health-check query is run.</p>
 */
public final class App {

    private static final String DEFAULT_QUERY = "SELECT 1";

    private App() {
    }

    public static void main(String[] args) {
        String sql = args.length > 0 ? String.join(" ", args) : DEFAULT_QUERY;
        Database database = Database.fromClasspath();

        try (Connection connection = database.connect();
             Statement statement = connection.createStatement();
             ResultSet results = statement.executeQuery(sql)) {
            print(results);
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    private static void print(ResultSet results) throws SQLException {
        ResultSetMetaData meta = results.getMetaData();
        int columns = meta.getColumnCount();

        StringJoiner header = new StringJoiner(" | ");
        for (int i = 1; i <= columns; i++) {
            header.add(meta.getColumnLabel(i));
        }
        System.out.println(header);

        while (results.next()) {
            StringJoiner row = new StringJoiner(" | ");
            for (int i = 1; i <= columns; i++) {
                row.add(String.valueOf(results.getString(i)));
            }
            System.out.println(row);
        }
    }
}
