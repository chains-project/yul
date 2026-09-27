package com.example.dbapp;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;

/**
 * Example entry point: connects to MySQL and runs a query, printing the rows.
 * Pass a SQL statement as arguments to run your own, e.g.
 * {@code mvn exec:java -Dexec.args="SELECT NOW()"}. Only read-only queries are
 * executed here.
 */
public final class App {

    private static final String DEFAULT_QUERY =
            "SELECT id, name, email FROM users ORDER BY id";

    private App() {
    }

    public static void main(String[] args) {
        String sql = args.length > 0 ? String.join(" ", args) : DEFAULT_QUERY;
        Database database = Database.fromConfig();

        try (Connection connection = database.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql);
             ResultSet rs = statement.executeQuery()) {

            System.out.printf("Connected to %s %s%n",
                    connection.getMetaData().getDatabaseProductName(),
                    connection.getMetaData().getDatabaseProductVersion());

            print(rs);
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static void print(ResultSet rs) throws SQLException {
        ResultSetMetaData meta = rs.getMetaData();
        int columns = meta.getColumnCount();

        StringBuilder header = new StringBuilder();
        for (int i = 1; i <= columns; i++) {
            if (i > 1) {
                header.append(" | ");
            }
            header.append(meta.getColumnLabel(i));
        }
        System.out.println(header);

        int rows = 0;
        while (rs.next()) {
            StringBuilder line = new StringBuilder();
            for (int i = 1; i <= columns; i++) {
                if (i > 1) {
                    line.append(" | ");
                }
                line.append(rs.getString(i));
            }
            System.out.println(line);
            rows++;
        }
        System.out.printf("(%d row%s)%n", rows, rows == 1 ? "" : "s");
    }
}
