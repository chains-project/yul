package com.example.demo.customer;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class CustomerService {

    private final CustomerRepository customers;

    public CustomerService(CustomerRepository customers) {
        this.customers = customers;
    }

    @Transactional(readOnly = true)
    public List<Customer> findAll() {
        return customers.findAll();
    }

    public Customer create(String name, String email) {
        return customers.save(new Customer(name, email));
    }
}
