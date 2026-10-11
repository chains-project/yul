package com.example.demo.customer;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsByEmail() {
        Customer saved = repository.save(new Customer("Ada Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();

        Optional<Customer> found = repository.findByEmailIgnoreCase("ADA@example.com");
        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Ada Lovelace");
    }

    @Test
    void reportsExistingEmail() {
        repository.save(new Customer("Grace Hopper", "grace@example.com"));

        assertThat(repository.existsByEmailIgnoreCase("grace@example.com")).isTrue();
        assertThat(repository.existsByEmailIgnoreCase("nobody@example.com")).isFalse();
    }
}
