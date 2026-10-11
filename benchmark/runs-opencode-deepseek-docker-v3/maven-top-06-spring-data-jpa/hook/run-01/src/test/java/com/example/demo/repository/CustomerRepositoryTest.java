package com.example.demo.repository;

import com.example.demo.domain.Customer;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsCustomerByEmail() {
        repository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        Optional<Customer> found = repository.findByEmailIgnoreCase("ADA@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getId()).isNotNull();
        assertThat(found.get().getCreatedAt()).isNotNull();
    }

    @Test
    void findsCustomersByLastName() {
        repository.save(new Customer("Ada", "Lovelace", "ada@example.com"));
        repository.save(new Customer("Grace", "Hopper", "grace@example.com"));
        repository.save(new Customer("Alan", "Turing", "alan@example.com"));

        List<Customer> result = repository.findByLastNameIgnoreCase("hopper");

        assertThat(result).extracting(Customer::getEmail).containsExactly("grace@example.com");
    }

    @Test
    void reportsExistingEmail() {
        repository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(repository.existsByEmailIgnoreCase("ada@example.com")).isTrue();
        assertThat(repository.existsByEmailIgnoreCase("missing@example.com")).isFalse();
    }
}
