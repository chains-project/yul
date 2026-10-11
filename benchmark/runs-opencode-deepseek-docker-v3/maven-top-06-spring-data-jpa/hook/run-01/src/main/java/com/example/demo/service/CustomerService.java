package com.example.demo.service;

import com.example.demo.domain.Customer;
import com.example.demo.repository.CustomerRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

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

    public Optional<Customer> findById(Long id) {
        return repository.findById(id);
    }

    public Optional<Customer> findByEmail(String email) {
        return repository.findByEmailIgnoreCase(email);
    }

    @Transactional
    public Customer create(Customer customer) {
        if (repository.existsByEmailIgnoreCase(customer.getEmail())) {
            throw new DuplicateEmailException(customer.getEmail());
        }
        return repository.save(customer);
    }

    @Transactional
    public Customer update(Long id, Customer changes) {
        Customer customer = repository.findById(id)
                .orElseThrow(() -> new CustomerNotFoundException(id));
        repository.findByEmailIgnoreCase(changes.getEmail())
                .filter(existing -> !existing.getId().equals(id))
                .ifPresent(existing -> {
                    throw new DuplicateEmailException(changes.getEmail());
                });
        customer.setFirstName(changes.getFirstName());
        customer.setLastName(changes.getLastName());
        customer.setEmail(changes.getEmail());
        return repository.save(customer);
    }

    @Transactional
    public void delete(Long id) {
        if (!repository.existsById(id)) {
            throw new CustomerNotFoundException(id);
        }
        repository.deleteById(id);
    }
}
