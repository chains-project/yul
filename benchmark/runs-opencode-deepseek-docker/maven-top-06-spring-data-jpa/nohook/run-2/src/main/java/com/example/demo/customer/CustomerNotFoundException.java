package com.example.demo.customer;

public class CustomerNotFoundException extends RuntimeException {

    public CustomerNotFoundException(Long id) {
        super("Customer not found: " + id);
    }
}
