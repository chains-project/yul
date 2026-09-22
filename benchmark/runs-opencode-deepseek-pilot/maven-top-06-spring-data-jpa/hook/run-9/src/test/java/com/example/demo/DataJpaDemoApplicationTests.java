package com.example.demo;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import com.example.demo.customer.Customer;
import com.example.demo.customer.CustomerRepository;

@SpringBootTest
class DataJpaDemoApplicationTests {

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void contextLoads() {
        assertThat(customerRepository).isNotNull();
    }

    @Test
    void savesAndFindsCustomer() {
        Customer saved = customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

        assertThat(saved.getId()).isNotNull();
        assertThat(customerRepository.findByEmail("ada@example.com")).isPresent();
        assertThat(customerRepository.findByLastName("Lovelace")).hasSize(1);
    }
}
