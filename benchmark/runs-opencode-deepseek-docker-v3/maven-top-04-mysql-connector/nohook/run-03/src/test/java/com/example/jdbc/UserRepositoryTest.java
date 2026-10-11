package com.example.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Exercises {@link UserRepository} against an in-memory H2 database running
 * in MySQL compatibility mode. No external MySQL server is required.
 */
class UserRepositoryTest {

    private UserRepository repository;

    @BeforeEach
    void setUp() throws SQLException {
        DbConfig config = DbConfig.of(
                "jdbc:h2:mem:testdb;MODE=MySQL;DB_CLOSE_DELAY=-1", "sa", "");
        Database database = new Database(config);
        try (Connection connection = database.connect();
             Statement statement = connection.createStatement()) {
            statement.execute("DROP TABLE IF EXISTS users");
            statement.execute("""
                    CREATE TABLE users (
                        id       BIGINT       NOT NULL AUTO_INCREMENT,
                        username VARCHAR(64)  NOT NULL,
                        email    VARCHAR(255) NOT NULL,
                        PRIMARY KEY (id)
                    )
                    """);
        }
        repository = new UserRepository(database);
    }

    @Test
    void insertThenFindById() throws SQLException {
        User created = repository.insert("carol", "carol@example.com");

        Optional<User> found = repository.findById(created.id());
        assertTrue(found.isPresent());
        assertEquals("carol", found.get().username());
    }

    @Test
    void findAllReturnsInsertedRows() throws SQLException {
        repository.insert("alice", "alice@example.com");
        repository.insert("bob", "bob@example.com");

        List<User> users = repository.findAll();
        assertEquals(2, users.size());
        assertEquals("alice", users.get(0).username());
    }
}
