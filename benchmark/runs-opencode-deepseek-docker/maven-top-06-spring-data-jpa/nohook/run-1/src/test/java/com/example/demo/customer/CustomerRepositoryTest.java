package com.example.demo.customer;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customers;

    @Test
    void savesAndFindsByEmail() {
        Customer saved = customers.save(new Customer("Ada Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();
        assertThat(customers.findByEmail("ada@example.com"))
                .isPresent()
                .get()
                .extracting(Customer::getName)
                .isEqualTo("Ada Lovelace");
    }
}
