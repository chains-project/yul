package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

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
    void findsByNameContainingIgnoreCase() {
        repository.save(new Customer("Grace Hopper", "grace@example.com"));
        repository.save(new Customer("Alan Turing", "alan@example.com"));

        List<Customer> matches = repository.findByNameContainingIgnoreCase("hopp");

        assertThat(matches).extracting(Customer::getEmail).containsExactly("grace@example.com");
    }

}
