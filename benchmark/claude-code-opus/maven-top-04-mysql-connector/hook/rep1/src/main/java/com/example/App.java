package com.example;

import com.example.db.Database;
import com.example.db.DatabaseConfig;
import com.example.db.User;
import com.example.db.UserRepository;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public final class App {

    public static void main(String[] args) {
        DatabaseConfig config = DatabaseConfig.fromEnvironment();
        Database database = new Database(config);
        System.out.println("Connecting with " + config);

        try {
            try (Connection conn = database.getConnection();
                 Statement stmt = conn.createStatement();
                 ResultSet rs = stmt.executeQuery("SELECT VERSION()")) {
                rs.next();
                System.out.println("Connected to MySQL " + rs.getString(1));
            }

            UserRepository users = new UserRepository(database);
            for (User user : users.findAll()) {
                System.out.println(user);
            }
        } catch (SQLException e) {
            System.err.printf("Database error (SQLState %s, code %d): %s%n",
                    e.getSQLState(), e.getErrorCode(), e.getMessage());
            System.exit(1);
        }
    }
}
