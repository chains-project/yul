package com.example.demo.customer;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsCustomersByLastName() {
        repository.save(new Customer("Ada", "Lovelace"));
        repository.save(new Customer("Grace", "Hopper"));

        List<Customer> found = repository.findByLastName("Hopper");

        assertThat(found).hasSize(1);
        assertThat(found.get(0).getFirstName()).isEqualTo("Grace");
    }
}
