package com.example.dbapp;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class CustomerDao {

    private final Database database;

    public CustomerDao(Database database) {
        this.database = database;
    }

    public List<Customer> findAll() throws SQLException {
        String sql = "SELECT id, name, email FROM customers ORDER BY id";
        List<Customer> customers = new ArrayList<>();
        try (Connection connection = database.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql);
             ResultSet resultSet = statement.executeQuery()) {
            while (resultSet.next()) {
                customers.add(map(resultSet));
            }
        }
        return customers;
    }

    public Optional<Customer> findById(long id) throws SQLException {
        String sql = "SELECT id, name, email FROM customers WHERE id = ?";
        try (Connection connection = database.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setLong(1, id);
            try (ResultSet resultSet = statement.executeQuery()) {
                return resultSet.next() ? Optional.of(map(resultSet)) : Optional.empty();
            }
        }
    }

    public long insert(Customer customer) throws SQLException {
        String sql = "INSERT INTO customers (name, email) VALUES (?, ?)";
        try (Connection connection = database.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            statement.setString(1, customer.name());
            statement.setString(2, customer.email());
            statement.executeUpdate();
            try (ResultSet generatedKeys = statement.getGeneratedKeys()) {
                if (generatedKeys.next()) {
                    return generatedKeys.getLong(1);
                }
            }
        }
        throw new SQLException("Insert did not return a generated key");
    }

    private static Customer map(ResultSet resultSet) throws SQLException {
        return new Customer(
                resultSet.getLong("id"),
                resultSet.getString("name"),
                resultSet.getString("email"));
    }
}
