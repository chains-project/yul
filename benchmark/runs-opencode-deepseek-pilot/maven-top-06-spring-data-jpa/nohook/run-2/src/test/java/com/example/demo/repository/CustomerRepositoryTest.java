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
    private CustomerRepository repository;

    @Test
    void savesAndFindsCustomerByLastName() {
        repository.save(new Customer("Ada", "Lovelace", "ada@example.com"));
        repository.save(new Customer("Grace", "Hopper", "grace@example.com"));

        List<Customer> result = repository.findByLastName("Hopper");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getFirstName()).isEqualTo("Grace");
    }

    @Test
    void findsCustomerByEmail() {
        Customer saved = repository.save(new Customer("Alan", "Turing", "alan@example.com"));

        Optional<Customer> result = repository.findByEmail("alan@example.com");

        assertThat(result).isPresent();
        assertThat(result.get().getId()).isEqualTo(saved.getId());
    }
}
