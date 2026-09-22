package com.example.demo.repository;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.demo.domain.Customer;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void savesAndFindsCustomerByEmail() {
        Customer saved = customerRepository.save(new Customer("Ada Lovelace", "ada@example.com"));

        Optional<Customer> found = customerRepository.findByEmail("ada@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getId()).isEqualTo(saved.getId());
        assertThat(found.get().getName()).isEqualTo("Ada Lovelace");
    }

    @Test
    void findsCustomersByNameIgnoringCase() {
        customerRepository.save(new Customer("Grace Hopper", "grace@example.com"));
        customerRepository.save(new Customer("Alan Turing", "alan@example.com"));

        List<Customer> results = customerRepository.findByNameContainingIgnoreCase("hopper");

        assertThat(results).extracting(Customer::getEmail).containsExactly("grace@example.com");
    }
}
