package com.example.demo.customer;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsByEmail() {
        repository.save(new Customer("Ada Lovelace", "ada@example.com"));

        assertThat(repository.findByEmail("ada@example.com"))
                .isPresent()
                .get()
                .extracting(Customer::getName)
                .isEqualTo("Ada Lovelace");
    }

    @Test
    void findsByNameIgnoringCase() {
        repository.save(new Customer("Grace Hopper", "grace@example.com"));

        assertThat(repository.findByNameContainingIgnoreCase("hopper")).hasSize(1);
    }
}
