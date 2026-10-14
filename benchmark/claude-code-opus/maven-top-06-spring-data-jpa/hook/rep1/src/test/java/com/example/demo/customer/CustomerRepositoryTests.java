package com.example.demo.customer;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class CustomerRepositoryTests {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsByEmail() {
        Customer saved = repository.save(new Customer("Ada Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();
        assertThat(repository.findByEmail("ada@example.com"))
                .get()
                .extracting(Customer::getName)
                .isEqualTo("Ada Lovelace");
    }

    @Test
    void searchesByNameIgnoringCase() {
        repository.save(new Customer("Grace Hopper", "grace@example.com"));
        repository.save(new Customer("Alan Turing", "alan@example.com"));

        assertThat(repository.findByNameContainingIgnoreCase("hop"))
                .extracting(Customer::getEmail)
                .containsExactly("grace@example.com");
    }
}
