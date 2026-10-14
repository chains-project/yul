package com.example.demo.customer;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTests {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsByEmail() {
        Customer saved = repository.save(new Customer("Ada Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();
        assertThat(repository.findByEmail("ada@example.com"))
                .hasValueSatisfying(c -> assertThat(c.getName()).isEqualTo("Ada Lovelace"));
    }

    @Test
    void findsByNameIgnoringCase() {
        repository.save(new Customer("Ada Lovelace", "ada@example.com"));
        repository.save(new Customer("Alan Turing", "alan@example.com"));

        assertThat(repository.findByNameContainingIgnoreCase("LOVE"))
                .extracting(Customer::getEmail)
                .containsExactly("ada@example.com");
    }
}
