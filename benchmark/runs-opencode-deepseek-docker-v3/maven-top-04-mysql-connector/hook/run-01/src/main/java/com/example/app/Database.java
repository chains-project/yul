package com.example.app;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.StringJoiner;

public final class Database implements AutoCloseable {

    private final Connection connection;

    private Database(Connection connection) {
        this.connection = connection;
    }

    public static Database connect(DbConfig config) throws SQLException {
        Connection connection = DriverManager.getConnection(
                config.jdbcUrl(), config.user(), config.password());
        return new Database(connection);
    }

    public List<String> listTables() throws SQLException {
        List<String> tables = new ArrayList<>();
        try (Statement statement = connection.createStatement();
             ResultSet resultSet = statement.executeQuery("SHOW TABLES")) {
            while (resultSet.next()) {
                tables.add(resultSet.getString(1));
            }
        }
        return tables;
    }

    public List<String> query(String sql) throws SQLException {
        List<String> rows = new ArrayList<>();
        try (Statement statement = connection.createStatement();
             ResultSet resultSet = statement.executeQuery(sql)) {
            ResultSetMetaData meta = resultSet.getMetaData();
            int columnCount = meta.getColumnCount();
            while (resultSet.next()) {
                StringJoiner joiner = new StringJoiner(", ", "{", "}");
                for (int i = 1; i <= columnCount; i++) {
                    joiner.add(meta.getColumnLabel(i) + "=" + resultSet.getString(i));
                }
                rows.add(joiner.toString());
            }
        }
        return rows;
    }

    @Override
    public void close() throws SQLException {
        connection.close();
    }
}
