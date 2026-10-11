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
    void savesAndFindsCustomerByEmail() {
        repository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(repository.findByEmail("ada@example.com"))
                .isPresent()
                .get()
                .extracting(Customer::getLastName)
                .isEqualTo("Lovelace");
    }

    @Test
    void searchesByFirstNamePrefixIgnoringCase() {
        repository.saveAll(List.of(
                new Customer("Grace", "Hopper", "grace@example.com"),
                new Customer("Alan", "Turing", "alan@example.com")));

        assertThat(repository.searchByFirstNameStartingWith("gr"))
                .singleElement()
                .extracting(Customer::getEmail)
                .isEqualTo("grace@example.com");
    }
}
