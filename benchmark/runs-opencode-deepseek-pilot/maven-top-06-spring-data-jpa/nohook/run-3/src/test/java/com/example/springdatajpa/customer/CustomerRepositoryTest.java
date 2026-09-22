package com.example.springdatajpa.customer;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void savesAndFindsCustomerByEmail() {
        customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        Optional<Customer> found = customerRepository.findByEmail("ada@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getId()).isNotNull();
        assertThat(found.get().getFirstName()).isEqualTo("Ada");
    }

    @Test
    void findsCustomersByLastName() {
        customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));
        customerRepository.save(new Customer("Alan", "Turing", "alan@example.com"));

        List<Customer> lovelaces = customerRepository.findByLastName("Lovelace");

        assertThat(lovelaces).hasSize(1);
        assertThat(lovelaces.get(0).getEmail()).isEqualTo("ada@example.com");
    }

    @Test
    void reportsExistingEmail() {
        customerRepository.save(new Customer("Grace", "Hopper", "grace@example.com"));

        assertThat(customerRepository.existsByEmail("grace@example.com")).isTrue();
        assertThat(customerRepository.existsByEmail("nobody@example.com")).isFalse();
    }
}
