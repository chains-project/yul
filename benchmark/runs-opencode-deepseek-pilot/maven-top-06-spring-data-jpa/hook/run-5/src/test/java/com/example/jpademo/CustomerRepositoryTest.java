package com.example.jpademo;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.jpademo.entity.Customer;
import com.example.jpademo.repository.CustomerRepository;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customers;

    @Test
    void savesAndFindsByEmail() {
        customers.save(new Customer("Alice", "alice@example.com"));

        assertThat(customers.findByEmail("alice@example.com"))
                .isPresent()
                .get()
                .extracting(Customer::getName)
                .isEqualTo("Alice");
    }

    @Test
    void findsByNameContainingIgnoreCase() {
        customers.save(new Customer("Alice", "alice@example.com"));
        customers.save(new Customer("Bob", "bob@example.com"));

        List<Customer> found = customers.findByNameContainingIgnoreCase("ali");

        assertThat(found).hasSize(1);
        assertThat(found.get(0).getEmail()).isEqualTo("alice@example.com");
    }
}
