package com.example.jpademo;

import com.example.jpademo.entity.Customer;
import com.example.jpademo.repository.CustomerRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private final CustomerRepository customers;

    public DataInitializer(CustomerRepository customers) {
        this.customers = customers;
    }

    @Override
    public void run(String... args) {
        if (customers.count() > 0) {
            return;
        }

        customers.save(new Customer("Alice", "alice@example.com"));
        customers.save(new Customer("Bob", "bob@example.com"));

        customers.findAll().forEach(System.out::println);
        customers.findByEmail("alice@example.com")
                .ifPresent(c -> System.out.println("Found by email: " + c));
    }
}
