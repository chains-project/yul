package com.example.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class MySQLConnector {

    private static final String URL = "jdbc:mysql://localhost:3306/mydatabase";
    private static final String USER = "root";
    private static final String PASSWORD = "password";

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }

    public void createTable() {
        String sql = "CREATE TABLE IF NOT EXISTS users ("
                   + "id INT AUTO_INCREMENT PRIMARY KEY,"
                   + "name VARCHAR(100) NOT NULL,"
                   + "email VARCHAR(100) UNIQUE NOT NULL"
                   + ")";

        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
            System.out.println("Table 'users' created successfully.");
        } catch (SQLException e) {
            System.err.println("Error creating table: " + e.getMessage());
        }
    }

    public void insertUser(String name, String email) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?)";

        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, name);
            pstmt.setString(2, email);
            pstmt.executeUpdate();
            System.out.println("User inserted: " + name + " (" + email + ")");
        } catch (SQLException e) {
            System.err.println("Error inserting user: " + e.getMessage());
        }
    }

    public void queryUsers() {
        String sql = "SELECT id, name, email FROM users";

        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            System.out.println("ID\tName\tEmail");
            System.out.println("---------------------------");
            while (rs.next()) {
                int id = rs.getInt("id");
                String name = rs.getString("name");
                String email = rs.getString("email");
                System.out.println(id + "\t" + name + "\t" + email);
            }
        } catch (SQLException e) {
            System.err.println("Error querying users: " + e.getMessage());
        }
    }

    public void updateUser(int id, String name, String email) {
        String sql = "UPDATE users SET name = ?, email = ? WHERE id = ?";

        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, name);
            pstmt.setString(2, email);
            pstmt.setInt(3, id);
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Rows updated: " + rowsAffected);
        } catch (SQLException e) {
            System.err.println("Error updating user: " + e.getMessage());
        }
    }

    public void deleteUser(int id) {
        String sql = "DELETE FROM users WHERE id = ?";

        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Rows deleted: " + rowsAffected);
        } catch (SQLException e) {
            System.err.println("Error deleting user: " + e.getMessage());
        }
    }

    public void searchUsers(String nameKeyword) {
        String sql = "SELECT id, name, email FROM users WHERE name LIKE ?";

        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, "%" + nameKeyword + "%");
            ResultSet rs = pstmt.executeQuery();

            System.out.println("Search results for '" + nameKeyword + "':");
            System.out.println("ID\tName\tEmail");
            System.out.println("---------------------------");
            while (rs.next()) {
                int id = rs.getInt("id");
                String name = rs.getString("name");
                String email = rs.getString("email");
                System.out.println(id + "\t" + name + "\t" + email);
            }
        } catch (SQLException e) {
            System.err.println("Error searching users: " + e.getMessage());
        }
    }

    public void closeConnection(Connection conn) {
        try {
            if (conn != null && !conn.isClosed()) {
                conn.close();
                System.out.println("Database connection closed.");
            }
        } catch (SQLException e) {
            System.err.println("Error closing connection: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        MySQLConnector connector = new MySQLConnector();

        System.out.println("=== MySQL JDBC Demo ===\n");

        try {
            Connection conn = connector.getConnection();
            System.out.println("Connected to database successfully!\n");

            connector.createTable();
            connector.insertUser("Alice Johnson", "alice@example.com");
            connector.insertUser("Bob Smith", "bob@example.com");
            connector.insertUser("Charlie Brown", "charlie@example.com");

            System.out.println("\n--- All Users ---");
            connector.queryUsers();

            System.out.println("\n--- Update User ---");
            connector.updateUser(1, "Alice Updated", "alice.new@example.com");
            connector.queryUsers();

            System.out.println("\n--- Search Users ---");
            connector.searchUsers("Alice");

            System.out.println("\n--- Delete User ---");
            connector.deleteUser(3);
            connector.queryUsers();

            connector.closeConnection(conn);

        } catch (SQLException e) {
            System.err.println("Database connection failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}