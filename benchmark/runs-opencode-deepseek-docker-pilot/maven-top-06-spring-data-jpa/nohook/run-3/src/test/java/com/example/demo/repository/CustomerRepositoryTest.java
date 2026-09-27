package com.example.demo.repository;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.demo.domain.Customer;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsByEmail() {
        Customer saved = repository.save(new Customer("Ada Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();

        Optional<Customer> found = repository.findByEmail("ada@example.com");
        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Ada Lovelace");
    }

    @Test
    void findsByNameIgnoringCase() {
        repository.save(new Customer("Grace Hopper", "grace@example.com"));
        repository.save(new Customer("Alan Turing", "alan@example.com"));

        assertThat(repository.findByNameContainingIgnoreCase("hopper"))
                .extracting(Customer::getEmail)
                .containsExactly("grace@example.com");
    }
}
