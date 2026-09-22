package com.example.demo.repository;

import com.example.demo.domain.Customer;
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
        Customer saved = customerRepository.save(new Customer("Grace", "Hopper", "grace@example.com"));

        assertThat(saved.getId()).isNotNull();

        Optional<Customer> found = customerRepository.findByEmail("grace@example.com");
        assertThat(found).isPresent();
        assertThat(found.get().getLastName()).isEqualTo("Hopper");
    }

    @Test
    void findsCustomersByLastName() {
        customerRepository.save(new Customer("Alan", "Turing", "alan@example.com"));
        customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        List<Customer> turings = customerRepository.findByLastName("Turing");

        assertThat(turings).hasSize(1);
        assertThat(turings.get(0).getFirstName()).isEqualTo("Alan");
    }
}
