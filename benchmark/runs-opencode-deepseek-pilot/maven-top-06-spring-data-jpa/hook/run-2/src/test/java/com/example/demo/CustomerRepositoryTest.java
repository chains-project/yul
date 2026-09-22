package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void savesAndFindsCustomersByLastName() {
        customerRepository.save(new Customer("Jane", "Doe"));
        customerRepository.save(new Customer("John", "Doe"));
        customerRepository.save(new Customer("Alice", "Smith"));

        List<Customer> does = customerRepository.findByLastName("Doe");

        assertThat(does).hasSize(2);
        assertThat(does).extracting(Customer::getFirstName).containsExactlyInAnyOrder("Jane", "John");
        assertThat(customerRepository.findById(does.get(0).getId())).isPresent();
    }

}
