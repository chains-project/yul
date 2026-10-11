package com.example.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public final class App {

    private static final String QUERY = "SELECT id, name FROM users ORDER BY id LIMIT ?";

    public static void main(String[] args) throws SQLException {
        DatabaseConfig config = DatabaseConfig.fromEnvironment();

        System.out.println("Connecting to " + config.url());

        try (Connection connection = DriverManager.getConnection(
                config.url(), config.username(), config.password())) {

            System.out.println("Connected: " + connection.getMetaData().getDatabaseProductVersion());

            try (PreparedStatement statement = connection.prepareStatement(QUERY)) {
                statement.setInt(1, 10);

                try (ResultSet resultSet = statement.executeQuery()) {
                    while (resultSet.next()) {
                        long id = resultSet.getLong("id");
                        String name = resultSet.getString("name");
                        System.out.printf("%d\t%s%n", id, name);
                    }
                }
            }
        }
    }
}
