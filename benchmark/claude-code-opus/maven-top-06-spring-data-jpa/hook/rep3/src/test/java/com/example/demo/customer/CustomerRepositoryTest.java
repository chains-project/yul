package com.example.demo.customer;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customers;

    @Test
    void savesAndFindsByEmail() {
        Customer saved = customers.save(new Customer("Ada Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();
        assertThat(customers.findByEmail("ada@example.com"))
                .get()
                .extracting(Customer::getName)
                .isEqualTo("Ada Lovelace");
    }

    @Test
    void findsByPartialNameIgnoringCase() {
        customers.save(new Customer("Ada Lovelace", "ada@example.com"));
        customers.save(new Customer("Alan Turing", "alan@example.com"));

        assertThat(customers.findByNameContainingIgnoreCase("LOVE"))
                .extracting(Customer::getEmail)
                .containsExactly("ada@example.com");
    }
}
