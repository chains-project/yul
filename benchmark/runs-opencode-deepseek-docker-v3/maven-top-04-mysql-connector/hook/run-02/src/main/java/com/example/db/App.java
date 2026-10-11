package com.example.db;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;

public class App {

    public static void main(String[] args) throws IOException, SQLException {
        Properties config = loadConfig();

        String host = config.getProperty("db.host", "localhost");
        int port = Integer.parseInt(config.getProperty("db.port", "3306"));
        String database = config.getProperty("db.name");
        String user = config.getProperty("db.user");
        String password = config.getProperty("db.password");
        String query = config.getProperty("db.query", "SELECT 1 AS ok");

        String url = Database.jdbcUrl(host, port, database);

        try (Connection connection = Database.connect(url, user, password);
             Statement statement = connection.createStatement();
             ResultSet resultSet = statement.executeQuery(query)) {

            System.out.println("Connected to " + url);
            printResultSet(resultSet);
        }
    }

    private static Properties loadConfig() throws IOException {
        Properties properties = new Properties();
        try (InputStream in = App.class.getResourceAsStream("/db.properties")) {
            if (in != null) {
                properties.load(in);
            }
        }
        overrideFromEnv(properties, "db.host", "DB_HOST");
        overrideFromEnv(properties, "db.port", "DB_PORT");
        overrideFromEnv(properties, "db.name", "DB_NAME");
        overrideFromEnv(properties, "db.user", "DB_USER");
        overrideFromEnv(properties, "db.password", "DB_PASSWORD");
        overrideFromEnv(properties, "db.query", "DB_QUERY");
        return properties;
    }

    private static void overrideFromEnv(Properties properties, String key, String envName) {
        String value = System.getenv(envName);
        if (value != null && !value.isBlank()) {
            properties.setProperty(key, value);
        }
    }

    private static void printResultSet(ResultSet resultSet) throws SQLException {
        ResultSetMetaData meta = resultSet.getMetaData();
        int columns = meta.getColumnCount();

        while (resultSet.next()) {
            StringBuilder row = new StringBuilder();
            for (int i = 1; i <= columns; i++) {
                if (i > 1) {
                    row.append(" | ");
                }
                row.append(meta.getColumnLabel(i)).append('=').append(resultSet.getString(i));
            }
            System.out.println(row);
        }
    }
}
