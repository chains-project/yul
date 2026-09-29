package com.example.demo.customer;

import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class CustomerService {

    private final CustomerRepository repository;

    public CustomerService(CustomerRepository repository) {
        this.repository = repository;
    }

    public List<Customer> findAll() {
        return repository.findAll();
    }

    public Customer findById(Long id) {
        return repository.findById(id)
                .orElseThrow(() -> new CustomerNotFoundException(id));
    }

    @Transactional
    public Customer create(String name, String email) {
        repository.findByEmail(email).ifPresent(existing -> {
            throw new IllegalArgumentException("Email already in use: " + email);
        });
        return repository.save(new Customer(name, email));
    }

    @Transactional
    public Customer update(Long id, String name, String email) {
        Customer customer = findById(id);
        customer.setName(name);
        customer.setEmail(email);
        return customer;
    }

    @Transactional
    public void delete(Long id) {
        if (!repository.existsById(id)) {
            throw new CustomerNotFoundException(id);
        }
        repository.deleteById(id);
    }
}
