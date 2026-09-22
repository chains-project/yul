package com.example.demo.repository;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.demo.domain.Customer;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void savesAndFindsCustomerByEmail() {
        Customer saved = customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();

        Optional<Customer> found = customerRepository.findByEmailIgnoreCase("ADA@example.com");
        assertThat(found).contains(saved);
    }

    @Test
    void findsCustomersByLastName() {
        customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));
        customerRepository.save(new Customer("Charles", "Babbage", "charles@example.com"));

        List<Customer> result = customerRepository.findByLastNameIgnoreCase("lovelace");

        assertThat(result)
                .hasSize(1)
                .extracting(Customer::getEmail)
                .containsExactly("ada@example.com");
    }

    @Test
    void reportsExistingEmail() {
        customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(customerRepository.existsByEmailIgnoreCase("ada@example.com")).isTrue();
        assertThat(customerRepository.existsByEmailIgnoreCase("nobody@example.com")).isFalse();
    }
}
