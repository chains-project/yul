package com.example.demo.repository;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import com.example.demo.domain.Customer;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void savesAndFindsCustomerByEmail() {
        Customer saved = customerRepository.save(
                new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();
        assertThat(saved.getCreatedAt()).isNotNull();

        Optional<Customer> found = customerRepository.findByEmail("ada@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getFirstName()).isEqualTo("Ada");
    }

    @Test
    void detectsExistingEmail() {
        customerRepository.save(new Customer("Alan", "Turing", "alan@example.com"));

        assertThat(customerRepository.existsByEmail("alan@example.com")).isTrue();
        assertThat(customerRepository.existsByEmail("missing@example.com")).isFalse();
    }
}
