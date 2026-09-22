package com.example.demo.customer;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsByLastName() {
        repository.save(new Customer("Alice", "Smith"));
        repository.save(new Customer("Bob", "Jones"));

        List<Customer> smiths = repository.findByLastName("Smith");

        assertThat(smiths).hasSize(1);
        assertThat(smiths.get(0).getFirstName()).isEqualTo("Alice");
    }

    @Test
    void findsByFirstNameContainingIgnoreCase() {
        repository.save(new Customer("Alice", "Smith"));
        repository.save(new Customer("Alicia", "Keys"));
        repository.save(new Customer("Bob", "Jones"));

        List<Customer> results = repository.findByFirstNameContainingIgnoreCase("ali");

        assertThat(results).hasSize(2);
    }
}
