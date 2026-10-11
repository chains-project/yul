package com.example.jdbc;

import java.sql.SQLException;
import java.util.List;

public final class Main {

    public static void main(String[] args) {
        DbConfig config = DbConfig.load();
        Database database = new Database(config);
        UserRepository users = new UserRepository(database);

        try {
            List<User> all = users.findAll();
            System.out.println("Connected to " + config.url());
            System.out.printf("Found %d user(s):%n", all.size());
            all.forEach(u -> System.out.printf("  #%d %s <%s>%n", u.id(), u.username(), u.email()));
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            System.exit(1);
        }
    }
}
