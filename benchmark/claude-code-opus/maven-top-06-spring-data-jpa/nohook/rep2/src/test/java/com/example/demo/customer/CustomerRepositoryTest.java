package com.example.demo.customer;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository repository;

    @Test
    void savesAndFindsCustomerByEmail() {
        Customer saved = repository.save(new Customer("Ada Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();
        assertThat(repository.findByEmail("ada@example.com"))
                .get()
                .extracting(Customer::getName)
                .isEqualTo("Ada Lovelace");
    }
}
