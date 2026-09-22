package com.example.demo.customer;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void savesAndFindsCustomerById() {
        Customer saved = customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();
        Optional<Customer> found = customerRepository.findById(saved.getId());
        assertThat(found).isPresent();
        assertThat(found.get().getEmail()).isEqualTo("ada@example.com");
    }

    @Test
    void findsByEmail() {
        customerRepository.save(new Customer("Grace", "Hopper", "grace@example.com"));

        Optional<Customer> found = customerRepository.findByEmail("grace@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getFirstName()).isEqualTo("Grace");
    }

    @Test
    void findsByLastName() {
        customerRepository.save(new Customer("Alan", "Turing", "alan@example.com"));
        customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        List<Customer> turings = customerRepository.findByLastName("Turing");

        assertThat(turings).hasSize(1);
        assertThat(turings.get(0).getEmail()).isEqualTo("alan@example.com");
    }

    @Test
    void reportsExistingEmail() {
        customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(customerRepository.existsByEmail("ada@example.com")).isTrue();
        assertThat(customerRepository.existsByEmail("nobody@example.com")).isFalse();
    }
}
