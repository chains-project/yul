package com.example.jpademo.repository;

import com.example.jpademo.model.Customer;
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
    void savesAndFindsCustomerByEmail() {
        Customer saved = customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();

        Optional<Customer> found = customerRepository.findByEmail("ada@example.com");
        assertThat(found).isPresent();
        assertThat(found.get().getFirstName()).isEqualTo("Ada");
    }

    @Test
    void findsCustomersByLastNameIgnoringCase() {
        customerRepository.save(new Customer("Grace", "Hopper", "grace@example.com"));
        customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        List<Customer> hoppers = customerRepository.findByLastNameIgnoreCase("hopper");

        assertThat(hoppers).hasSize(1);
        assertThat(hoppers.get(0).getEmail()).isEqualTo("grace@example.com");
    }

    @Test
    void reportsWhetherEmailExists() {
        customerRepository.save(new Customer("Grace", "Hopper", "grace@example.com"));

        assertThat(customerRepository.existsByEmail("grace@example.com")).isTrue();
        assertThat(customerRepository.existsByEmail("nobody@example.com")).isFalse();
    }
}
