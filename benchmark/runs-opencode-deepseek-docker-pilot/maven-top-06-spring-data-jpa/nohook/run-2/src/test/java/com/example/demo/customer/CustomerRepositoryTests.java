package com.example.demo.customer;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTests {

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void savesAndFindsByEmail() {
        customerRepository.save(new Customer("Ada Lovelace", "ada@example.com"));

        Optional<Customer> found = customerRepository.findByEmail("ada@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getId()).isNotNull();
        assertThat(found.get().getName()).isEqualTo("Ada Lovelace");
    }

    @Test
    void findsByNameContainingIgnoreCase() {
        customerRepository.save(new Customer("Grace Hopper", "grace@example.com"));

        assertThat(customerRepository.findByNameContainingIgnoreCase("hopper")).hasSize(1);
    }
}
