package com.example.dbapp;

import java.util.List;

public final class App {

    private App() {
    }

    public static void main(String[] args) {
        DatabaseConfig config = DatabaseConfig.load();
        Database database = new Database(config);
        CustomerDao customerDao = new CustomerDao(database);

        System.out.println("Connecting to " + config.url());

        try {
            List<Customer> customers = customerDao.findAll();
            System.out.println("Found " + customers.size() + " customer(s):");
            for (Customer customer : customers) {
                System.out.printf("  #%d %s <%s>%n", customer.id(), customer.name(), customer.email());
            }
        } catch (Exception e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
