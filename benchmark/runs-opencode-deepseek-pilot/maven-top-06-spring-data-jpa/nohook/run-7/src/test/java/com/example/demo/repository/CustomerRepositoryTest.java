package com.example.demo.repository;

import com.example.demo.domain.Customer;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void savesAndFindsCustomerByEmail() {
        entityManager.persist(new Customer("Ada", "Lovelace", "ada@example.com"));
        entityManager.flush();

        Optional<Customer> found = customerRepository.findByEmail("ada@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getFirstName()).isEqualTo("Ada");
        assertThat(found.get().getCreatedAt()).isNotNull();
    }

    @Test
    void findsCustomersByLastName() {
        entityManager.persist(new Customer("Ada", "Lovelace", "ada@example.com"));
        entityManager.persist(new Customer("Grace", "Hopper", "grace@example.com"));
        entityManager.persist(new Customer("Alan", "Turing", "alan@example.com"));
        entityManager.flush();

        List<Customer> result = customerRepository.findByLastName("Hopper");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getEmail()).isEqualTo("grace@example.com");
    }

    @Test
    void existsByEmailReturnsTrueOnlyForKnownEmail() {
        entityManager.persist(new Customer("Ada", "Lovelace", "ada@example.com"));
        entityManager.flush();

        assertThat(customerRepository.existsByEmail("ada@example.com")).isTrue();
        assertThat(customerRepository.existsByEmail("nobody@example.com")).isFalse();
    }
}
